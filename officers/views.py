import unicodedata

import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.contrib.auth.views import LoginView
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from officers.config import SHEET_TO_MODEL_FIELDS
from officers.constants import GENERAL_INFO_FIELDS, REQUIRED_FIELDS
from officers.utils import create_officer_related_objects, extract_officer_data

from . import forms as f
from . import models as m


@login_required
def officer_list(request):
    filter_fields = {
        "military_type": "military_type",
        "military_rank": "military_rank",
        "work_unit": "work_unit",
        "blood_type": "blood_type",
        "size_of_hat": "size_of_hat",
        "political_theory": "political_theory",
        "position": "position",
        "year_of_birth": "birth_year",
        "education": "education",
        "current_residence": "current_residence",
        "birth_place": "birth_place",
    }

    officers = m.Officer.objects.all()  # Start with all officers

    # Search by name
    query = request.GET.get("q")
    if query:
        normalized_query = unicodedata.normalize("NFC", query)
        officers = officers.filter(name__icontains=normalized_query)

    # Search by ID
    id_ca_query = request.GET.get("id_ca")
    if id_ca_query:
        # Trim the whitespace
        id_ca_query = id_ca_query.strip()
        officers = officers.filter(id_ca__icontains=id_ca_query)

    # Apply filters
    for field, filter_action in filter_fields.items():
        value = request.GET.get(field)
        if value:
            # If the filter action is a callable (e.g., lambda), call it
            if callable(filter_action):
                officers = filter_action(officers, value)
            else:
                # Otherwise, apply a simple filter
                officers = officers.filter(**{filter_action: value})

        if field == "year_of_birth":
            selected_year_of_birth = int(value) if value else None

    # Get unique sorted values for filter dropdowns
    dropdown_fields = {
        "military_types": "military_type",
        "military_ranks": "military_rank",
        "work_units": "work_unit",
        "blood_types": "blood_type",
        "political_theories": "political_theory",
        "hat_sizes": "size_of_hat",
        "positions": "position",
        "years_of_birth": "birth_year",
        "birth_places": "birth_place",
        "educations": "education",
        "current_residences": "current_residence",
    }

    context = {}
    for context_key, field in dropdown_fields.items():
        context[context_key] = sorted(
            filter(
                None, m.Officer.objects.values_list(field, flat=True).distinct()
            )
        )

    context["officers"] = officers
    context["query"] = query
    context["id_ca_query"] = id_ca_query
    context["selected_year_of_birth"] = selected_year_of_birth

    # Handle export functionality
    if request.method == "POST" and "export" in request.POST:
        form = f.OfficerExportForm(request.POST)
        if form.is_valid():
            selected_officers = form.cleaned_data["officers"]
            selected_fields = form.cleaned_data["fields"]

            # Filter officers based on selected IDs
            officers_to_export = officers.filter(pk__in=selected_officers)

            if not officers_to_export:
                messages.warning(request, "No officers selected for export.")
                return redirect("officer_list")

            # Retrieve data for selected officers and fields
            officers_data = []
            for idx, officer in enumerate(officers_to_export, start=1):
                row = {
                    "STT": idx,
                }
                for field in selected_fields:
                    row[field] = getattr(officer, field)

                officers_data.append(row)

            # Create a DataFrame with the selected fields
            df = pd.DataFrame(officers_data, columns=["STT"] + selected_fields)

            # Prepare the response as an Excel file
            response = HttpResponse(
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = (
                "attachment; filename=officers.xlsx"
            )

            with pd.ExcelWriter(response, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Officers")

            return response
    else:
        form = f.OfficerExportForm(initial={"officers": officers})

    context["form"] = form
    return render(request, "officers/officer_list.html", context)


@login_required
@permission_required("officers.add_officer", raise_exception=True)
def officer_create(request):
    if request.method == "POST":
        form = f.OfficerInfoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("officer_list")
    else:
        form = f.OfficerInfoForm()

    return render(request, "officers/officer_form.html", {"form": form})


@login_required
@permission_required("officers.add_officer", raise_exception=True)
def excel_upload(request):
    if request.method == "POST":
        form = f.ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist("files")

            for file in files:
                try:
                    data = pd.read_excel(file, "Thông tin chung")

                    # Iterate over the rows and create Officer objects
                    for index, row in data.iterrows():
                        officer_data, row_missing_fields, skip_row = (
                            extract_officer_data(
                                index,
                                row,
                                GENERAL_INFO_FIELDS,
                                REQUIRED_FIELDS,
                            )
                        )

                        if skip_row:
                            messages.warning(
                                request,
                                f"Skipping row {row_missing_fields['row']} due to missing fields: {', '.join(row_missing_fields['missing_fields'])}",  # noqa
                            )
                            continue

                        try:
                            officer = m.Officer.objects.create(**officer_data)
                        except IntegrityError as e:
                            if "officers_officer.id_ca" in str(e):
                                messages.warning(
                                    request,
                                    f"Skipping row {index + 1} due to duplicate with existing officer '{officer_data['birth_name']}' with ID '{officer_data['id_ca']}'",  # noqa
                                )
                            else:
                                messages.error(
                                    request,
                                    f"Error processing row {index + 1}: {str(e)}",
                                )
                            continue

                        # Create related objects for the officer
                        for sheet_name, config in SHEET_TO_MODEL_FIELDS.items():
                            model_class = config.model_class
                            fields = config.fields
                            create_officer_related_objects(
                                request=request,
                                officer=officer,
                                file=file,
                                sheet_name=sheet_name,
                                model_class=model_class,
                                fields=fields,
                                error_message_prefix=f"Error processing {sheet_name.lower()}",
                            )
                except Exception as e:
                    messages.error(
                        request, f"Error processing file {file.name}: {e}"
                    )
            return redirect("officer_list")
    else:
        form = f.ExcelUploadForm()

    return render(request, "officers/excel_upload_form.html", {"form": form})


@login_required
@permission_required("officers.change_officer", raise_exception=True)
def officer_update(request, pk):
    officer = get_object_or_404(m.Officer, pk=pk)

    if request.method == "POST":
        form = f.OfficerInfoForm(request.POST, instance=officer)
        if form.is_valid():
            form.save()
            return redirect("officer_list")
    else:
        form = f.OfficerInfoForm(instance=officer)

    return render(request, "officers/officer_form.html", {"form": form})


@login_required
def officer_detail(request, pk):
    officer = get_object_or_404(m.Officer, pk=pk)
    disciplines = officer.disciplines.all()
    context = {"officer": officer, "disciplines": disciplines}
    return render(request, "officers/officer_detail.html", context)


@login_required
@permission_required("officers.delete_officer", raise_exception=True)
def officer_delete(request, pk):
    officer = get_object_or_404(m.Officer, pk=pk)
    if request.method == "POST":
        officer.delete()
        return redirect("officer_list")
    return render(
        request, "officers/officer_confirm_delete.html", {"officer": officer}
    )


@login_required
@permission_required("officers.delete_officer", raise_exception=True)
def delete_all_officers(request):
    if request.method == "POST":
        m.Officer.objects.all().delete()
        return redirect("officer_list")
    return render(request, "officers/officer_confirm_delete_all.html")


def logout_page(request):
    return render(request, "registration/logout.html")


class CustomLoginView(LoginView):
    def get_success_url(self):
        # Can set a custom URL based on user role
        # if self.request.user.is_superuser:
        #     return reverse("admin_dashboard")
        return reverse("officer_list")


########################################################
# Officer Related Mixin
class OfficerRelatedMixin(LoginRequiredMixin):
    model = None  # Will be set in the view
    pk_url_kwarg = None  # Will be set in the view
    view_url = None  # Will be set in the view
    related_context_field: str = None

    def get_officer(self):
        return get_object_or_404(m.Officer, pk=self.kwargs["pk"])

    def get_object(self):
        # Dynamically get the object based on the model and primary key
        return get_object_or_404(
            self.model,
            pk=self.kwargs[self.pk_url_kwarg],
            officer=self.get_officer(),
        )

    def get_success_url(self):
        # Dynamically construct the URL to return to the officer's related list
        return reverse_lazy(self.view_url, kwargs={"pk": self.kwargs["pk"]})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        officer = self.get_officer()
        context["officer"] = officer
        context[self.related_context_field] = getattr(
            officer, self.related_context_field
        ).all()

        # Add the object ID to the context if editing (if the object exists)
        try:
            if self.related_context_field.endswith("ves"):
                singular_field = self.related_context_field[:-1]
            elif self.related_context_field.endswith("les"):
                singular_field = self.related_context_field[:-1]
            elif self.related_context_field.endswith("nes"):
                singular_field = self.related_context_field[:-1]
            elif self.related_context_field.endswith("ies"):
                singular_field = self.related_context_field[:-3] + "y"
            elif self.related_context_field.endswith("es"):
                singular_field = self.related_context_field[:-2]
            elif self.related_context_field.endswith("s"):
                singular_field = self.related_context_field[:-1]
            else:
                singular_field = self.related_context_field
                
            context[f"edit_{singular_field}_id"] = self.object.id
        except AttributeError:
            pass

        return context


########################################################
# Officer Titles


# Title Mixin
class TitleMixin(OfficerRelatedMixin):
    model = m.Title
    form_class = f.TitleForm
    view_url = "url_title_view"
    related_context_field = "titles"


# Title View
class TitleListView(TitleMixin, ListView):
    template_name = "officers/officer_title.html"
    context_object_name = "titles"

    def get_queryset(self):
        return self.get_officer().titles.all()


# Create Title
class TitleCreateView(PermissionRequiredMixin, TitleMixin, CreateView):
    template_name = "officers/officer_title_manage.html"
    permission_required = "officers.adjust_officer_title"

    def form_valid(self, form):
        form.instance.officer = self.get_officer()
        return super().form_valid(form)


# Update Title
class TitleUpdateView(PermissionRequiredMixin, TitleMixin, UpdateView):
    pk_url_kwarg = "title_pk"
    template_name = "officers/officer_title_manage.html"
    permission_required = "officers.adjust_officer_title"


# Delete Title
class TitleDeleteView(PermissionRequiredMixin, OfficerRelatedMixin, DeleteView):
    model = m.Title
    pk_url_kwarg = "title_pk"
    view_url = "url_title_view"
    related_context_field = "titles"
    permission_required = "officers.delete_officer_title"


########################################################
# Officer Position Plans


# Position Plan Mixin
class PositionPlanMixin(OfficerRelatedMixin):
    model = m.PositionPlan
    form_class = f.PositionPlanForm
    view_url = "url_position_plan"
    related_context_field = "position_plans"


# Position Plan View
class PositionPlanListView(PositionPlanMixin, ListView):
    template_name = "officers/position_plan.html"
    context_object_name = "position_plans"

    def get_queryset(self):
        return self.get_officer().position_plans.all()


# Create Position Plan
class PositionPlanCreateView(
    PermissionRequiredMixin,
    PositionPlanMixin,
    CreateView,
):
    template_name = "officers/position_plan_manage.html"
    permission_required = "officers.adjust_position_plan"

    def form_valid(self, form):
        form.instance.officer = self.get_officer()
        return super().form_valid(form)


# Update Position Plan
class PositionPlanUpdateView(
    PermissionRequiredMixin, PositionPlanMixin, UpdateView
):
    pk_url_kwarg = "position_plan_pk"
    template_name = "officers/position_plan_manage.html"
    permission_required = "officers.adjust_position_plan"


# Delete Position Plan
class PositionPlanDeleteView(
    PermissionRequiredMixin, OfficerRelatedMixin, DeleteView
):
    model = m.PositionPlan
    pk_url_kwarg = "position_plan_pk"
    view_url = "url_position_plan"
    related_context_field = "position_plans"
    permission_required = "officers.delete_officer_position_plan"


########################################################
# Officer Learning Paths


# Learning Path Mixin
class LearningPathMixin(OfficerRelatedMixin):
    model = m.LearningPath
    form_class = f.LearningPathForm
    view_url = "url_learning_path"
    related_context_field = "learning_paths"


# Learning Path View
class LearningPathListView(LearningPathMixin, ListView):
    template_name = "officers/officer_learning_path.html"
    context_object_name = "learning_paths"

    def get_queryset(self):
        return self.get_officer().learning_paths.all()


# Create Learning Path
class LearningPathCreateView(
    PermissionRequiredMixin,
    LearningPathMixin,
    CreateView,
):
    template_name = "officers/learning_path_manage.html"
    permission_required = "officers.adjust_learning_path"

    def form_valid(self, form):
        form.instance.officer = self.get_officer()
        return super().form_valid(form)


# Update Learning Path
class LearningPathUpdateView(
    PermissionRequiredMixin, LearningPathMixin, UpdateView
):
    pk_url_kwarg = "learning_path_pk"
    template_name = "officers/learning_path_manage.html"
    permission_required = "officers.adjust_learning_path"


# Delete Learning Path
class LearningPathDeleteView(
    PermissionRequiredMixin, OfficerRelatedMixin, DeleteView
):
    model = m.LearningPath
    pk_url_kwarg = "learning_path_pk"
    view_url = "url_learning_path"
    related_context_field = "learning_paths"
    permission_required = "officers.delete_officer_learning_path"


########################################################
# Officer Work Processes


# Work Process Mixin
class WorkProcessMixin(OfficerRelatedMixin):
    model = m.WorkProcess
    form_class = f.WorkProcessForm
    view_url = "url_work_process"
    related_context_field = "work_processes"


# Work Process View
class WorkProcessListView(WorkProcessMixin, ListView):
    template_name = "officers/officer_work_process.html"
    context_object_name = "work_processes"

    def get_queryset(self):
        return self.get_officer().work_processes.all()
    

# Create Work Process
class WorkProcessCreateView(
    PermissionRequiredMixin,
    WorkProcessMixin,
    CreateView,
):
    template_name = "officers/work_process_manage.html"
    permission_required = "officers.adjust_work_process"

    def form_valid(self, form):
        form.instance.officer = self.get_officer()
        return super().form_valid(form)
    

# Update Work Process
class WorkProcessUpdateView(
    PermissionRequiredMixin, WorkProcessMixin, UpdateView
):
    pk_url_kwarg = "work_process_pk"
    template_name = "officers/work_process_manage.html"
    permission_required = "officers.adjust_work_process"


# Delete Work Process
class WorkProcessDeleteView(
    PermissionRequiredMixin, OfficerRelatedMixin, DeleteView
):
    model = m.WorkProcess
    pk_url_kwarg = "work_process_pk"
    view_url = "url_work_process"
    related_context_field = "work_processes"
    permission_required = "officers.delete_officer_work_process"


########################################################
# Officer Salary Processes


# Salary Process Mixin
class SalaryProcessMixin(OfficerRelatedMixin):
    model = m.SalaryProcess
    form_class = f.SalaryProcessForm
    view_url = "url_salary_process"
    related_context_field = "salary_processes"


# Salary Process View
class SalaryProcessListView(SalaryProcessMixin, ListView):
    template_name = "officers/officer_salary_process.html"
    context_object_name = "salary_processes"

    def get_queryset(self):
        return self.get_officer().salary_processes.all()
    

# Create Salary Process
class SalaryProcessCreateView(
    PermissionRequiredMixin,
    SalaryProcessMixin,
    CreateView,
):
    template_name = "officers/salary_process_manage.html"
    permission_required = "officers.adjust_salary_process"

    def form_valid(self, form):
        form.instance.officer = self.get_officer()
        return super().form_valid(form)
    

# Update Salary Process
class SalaryProcessUpdateView(
    PermissionRequiredMixin, SalaryProcessMixin, UpdateView
):
    pk_url_kwarg = "salary_process_pk"
    template_name = "officers/salary_process_manage.html"
    permission_required = "officers.adjust_salary_process"


# Delete Salary Process
class SalaryProcessDeleteView(
    PermissionRequiredMixin, OfficerRelatedMixin, DeleteView
):
    model = m.SalaryProcess
    pk_url_kwarg = "salary_process_pk"
    view_url = "url_salary_process"
    related_context_field = "salary_processes"
    permission_required = "officers.delete_officer_salary_process"


########################################################
# Officer Laudatories


# Laudatory Mixin
class LaudatoryMixin(OfficerRelatedMixin):
    model = m.Laudatory
    form_class = f.LaudatoryForm
    view_url = "url_laudatory"
    related_context_field = "laudatories"


# Laudatory View
class LaudatoryListView(LaudatoryMixin, ListView):
    template_name = "officers/officer_laudatory.html"
    context_object_name = "laudatories"

    def get_queryset(self):
        return self.get_officer().laudatories.all()
    

# Create Laudatory
class LaudatoryCreateView(
    PermissionRequiredMixin,
    LaudatoryMixin,
    CreateView,
):
    template_name = "officers/laudatory_manage.html"
    permission_required = "officers.adjust_laudatory"

    def form_valid(self, form):
        form.instance.officer = self.get_officer()
        return super().form_valid(form)
    

# Update Laudatory
class LaudatoryUpdateView(
    PermissionRequiredMixin, LaudatoryMixin, UpdateView
):
    pk_url_kwarg = "laudatory_pk"
    template_name = "officers/laudatory_manage.html"
    permission_required = "officers.adjust_laudatory"

    
# Delete Laudatory
class LaudatoryDeleteView(
    PermissionRequiredMixin, OfficerRelatedMixin, DeleteView
):
    model = m.Laudatory
    pk_url_kwarg = "laudatory_pk"
    view_url = "url_laudatory"
    related_context_field = "laudatories"
    permission_required = "officers.delete_officer_laudatory"


########################################################
# Officer Disciplines


# Discipline Mixin
class DisciplineMixin(OfficerRelatedMixin):
    model = m.Discipline
    form_class = f.DisciplineForm
    view_url = "url_discipline"
    related_context_field = "disciplines"


# Discipline View
class DisciplineListView(DisciplineMixin, ListView):
    template_name = "officers/officer_discipline.html"
    context_object_name = "disciplines"

    def get_queryset(self):
        return self.get_officer().disciplines.all()
    

# Create Discipline
class DisciplineCreateView(
    PermissionRequiredMixin,
    DisciplineMixin,
    CreateView,
):
    template_name = "officers/discipline_manage.html"
    permission_required = "officers.adjust_discipline"

    def form_valid(self, form):
        form.instance.officer = self.get_officer()
        return super().form_valid(form)
    

# Update Discipline
class DisciplineUpdateView(
    PermissionRequiredMixin, DisciplineMixin, UpdateView
):
    pk_url_kwarg = "discipline_pk"
    template_name = "officers/discipline_manage.html"
    permission_required = "officers.adjust_discipline"


# Delete Discipline
class DisciplineDeleteView(
    PermissionRequiredMixin, OfficerRelatedMixin, DeleteView
):
    model = m.Discipline
    pk_url_kwarg = "discipline_pk"
    view_url = "url_discipline"
    related_context_field = "disciplines"
    permission_required = "officers.delete_officer_discipline"


########################################################
# Officer Relatives


# Relative Mixin
class RelativeMixin(OfficerRelatedMixin):
    model = m.Relative
    form_class = f.RelativeForm
    view_url = "url_relative"
    related_context_field = "relatives"


# Relative View
class RelativeListView(RelativeMixin, ListView):
    template_name = "officers/officer_relative.html"
    context_object_name = "relatives"

    def get_queryset(self):
        return self.get_officer().relatives.all()
    

# Create Relative
class RelativeCreateView(
    PermissionRequiredMixin,
    RelativeMixin,
    CreateView,
):
    template_name = "officers/relative_manage.html"
    permission_required = "officers.adjust_relative"

    def form_valid(self, form):
        form.instance.officer = self.get_officer()
        return super().form_valid(form) 
    

# Update Relative
class RelativeUpdateView(
    PermissionRequiredMixin, RelativeMixin, UpdateView
):
    pk_url_kwarg = "relative_pk"
    template_name = "officers/relative_manage.html"
    permission_required = "officers.adjust_relative"


# Delete Relative
class RelativeDeleteView(
    PermissionRequiredMixin, OfficerRelatedMixin, DeleteView
):
    model = m.Relative
    pk_url_kwarg = "relative_pk"
    view_url = "url_relative"
    related_context_field = "relatives"
    permission_required = "officers.delete_officer_relative"


########################################################
# Officer Abroads


# Abroad Mixin
class AbroadMixin(OfficerRelatedMixin):
    model = m.Abroad
    form_class = f.AbroadForm
    view_url = "url_abroad"
    related_context_field = "abroads"


# Abroad View
class AbroadListView(AbroadMixin, ListView):
    template_name = "officers/officer_abroad.html"
    context_object_name = "abroads"

    def get_queryset(self):
        return self.get_officer().abroads.all()
    

# Create Abroad
class AbroadCreateView(
    PermissionRequiredMixin,
    AbroadMixin,
    CreateView,
):
    template_name = "officers/abroad_manage.html"
    permission_required = "officers.adjust_abroad"

    def form_valid(self, form):
        form.instance.officer = self.get_officer()
        return super().form_valid(form)
    

# Update Abroad
class AbroadUpdateView(
    PermissionRequiredMixin, AbroadMixin, UpdateView
):
    pk_url_kwarg = "abroad_pk"
    template_name = "officers/abroad_manage.html"
    permission_required = "officers.adjust_abroad"


# Delete Abroad
class AbroadDeleteView(
    PermissionRequiredMixin, OfficerRelatedMixin, DeleteView
):
    model = m.Abroad
    pk_url_kwarg = "abroad_pk"
    view_url = "url_abroad"
    related_context_field = "abroads"
    permission_required = "officers.delete_officer_abroad"


########################################################
# Officer Army Join Histories


# Army Join History Mixin
class ArmyJoinHistoryMixin(OfficerRelatedMixin):
    model = m.ArmyJoinHistory
    form_class = f.ArmyJoinHistoryForm
    view_url = "url_army_join_history"
    related_context_field = "army_join_histories"


# Army Join History View
class ArmyJoinHistoryListView(ArmyJoinHistoryMixin, ListView):
    template_name = "officers/officer_army_join_history.html"
    context_object_name = "army_join_histories"

    def get_queryset(self):
        return self.get_officer().army_join_histories.all()
    

# Create Army Join History
class ArmyJoinHistoryCreateView(
    PermissionRequiredMixin,
    ArmyJoinHistoryMixin,
    CreateView,
):
    template_name = "officers/army_join_history_manage.html"
    permission_required = "officers.adjust_army_join_history"

    def form_valid(self, form):
        form.instance.officer = self.get_officer()
        return super().form_valid(form)
    

# Update Army Join History
class ArmyJoinHistoryUpdateView(
    PermissionRequiredMixin, ArmyJoinHistoryMixin, UpdateView
):
    pk_url_kwarg = "army_join_history_pk"
    template_name = "officers/army_join_history_manage.html"
    permission_required = "officers.adjust_army_join_history"


# Delete Army Join History
class ArmyJoinHistoryDeleteView(
    PermissionRequiredMixin, OfficerRelatedMixin, DeleteView
):
    model = m.ArmyJoinHistory
    pk_url_kwarg = "army_join_history_pk"
    view_url = "url_army_join_history"
    related_context_field = "army_join_histories"
    permission_required = "officers.delete_officer_army_join_history"


########################################################
# Officer Healths


# Health Mixin
class HealthMixin(OfficerRelatedMixin):
    model = m.Health
    form_class = f.HealthForm
    view_url = "url_health"
    related_context_field = "healths"


# Health View
class HealthListView(HealthMixin, ListView):
    template_name = "officers/officer_health.html"
    context_object_name = "healths"

    def get_queryset(self):
        return self.get_officer().healths.all()
    

# Create Health
class HealthCreateView(
    PermissionRequiredMixin,
    HealthMixin,
    CreateView,
):
    template_name = "officers/health_manage.html"
    permission_required = "officers.adjust_health"

    def form_valid(self, form):
        form.instance.officer = self.get_officer()
        return super().form_valid(form)
    

# Update Health
class HealthUpdateView(
    PermissionRequiredMixin, HealthMixin, UpdateView
):
    pk_url_kwarg = "health_pk"
    template_name = "officers/health_manage.html"
    permission_required = "officers.adjust_health"


# Delete Health
class HealthDeleteView(
    PermissionRequiredMixin, OfficerRelatedMixin, DeleteView
):
    model = m.Health
    pk_url_kwarg = "health_pk"
    view_url = "url_health"
    related_context_field = "healths"
    permission_required = "officers.delete_officer_health"
