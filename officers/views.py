import os
import unicodedata
import zipfile
from io import BytesIO

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
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from officers.config import SHEET_TO_MODEL_FIELDS
from officers.constants import (
    FILTER_FIELDS,
    GENERAL_INFO_FIELDS,
    IMAGES_CATEGORY,
    REQUIRED_FIELDS,
    SEARCH_FIELDS,
)
from officers.utils import (
    create_officer_related_objects,
    export_related_data,
    extract_officer_data,
)

from . import forms as f
from . import models as m


@login_required
def officer_list(request):
    context = {}

    officers = m.Officer.objects.all()  # Start with all officers

    # Search by multiple fields
    for field in SEARCH_FIELDS:
        query = request.GET.get(field)
        if query:
            query = query.strip()
            normalized_query = unicodedata.normalize("NFC", query)
            officers = officers.filter(
                **{f"{field}__icontains": normalized_query}
            )
            context[field] = query

    # Apply filters
    for field in FILTER_FIELDS:
        value = request.GET.get(field)
        context[field] = sorted(
            filter(
                None,
                m.Officer.objects.values_list(field, flat=True).distinct(),
            )
        )
        if value:
            officers = officers.filter(**{field: value})

    context["officers"] = officers

    # Initialize form for the template
    form = f.OfficerExportForm(initial={"officers": officers})
    context["form"] = form

    return render(request, "officers/officer_list.html", context)


@login_required
def export_officers_data(request):
    if request.method == "POST" and "export" in request.POST:
        form = f.OfficerExportForm(request.POST)
        
        if form.is_valid():
            selected_officers = form.cleaned_data["officers"]
            selected_fields = form.cleaned_data["model_fields"]
            selected_related_tables = form.cleaned_data["related_tables"]

            # Create an in-memory ZIP file to store the officer Excel files
            # no matter if related tables are selected
            in_memory_zip = BytesIO()
            with zipfile.ZipFile(in_memory_zip, "w") as zip_file:

                # Export general information of all selected officers to an Excel file
                officers_data_stack = []
                for index, officer in enumerate(selected_officers, start=1):
                    row = {
                        "STT": index
                    }  # Add numerical order as the first column
                    for field in selected_fields:
                        row[field] = getattr(officer, field)
                    officers_data_stack.append(row)

                # Create an in-memory Excel file for the selected officers
                officers_file = BytesIO()
                officers_filename = "thong_tin_CB.xlsx"

                with pd.ExcelWriter(officers_file, engine="openpyxl") as writer:
                    field_labels = ["STT"] + [
                        GENERAL_INFO_FIELDS.get(field, field)
                        for field in selected_fields
                    ]
                    df_officers = pd.DataFrame(officers_data_stack)
                    df_officers.columns = field_labels
                    df_officers.to_excel(
                        writer, index=False, sheet_name="Thông tin chung"
                    )

                # Ensure the Excel file is saved in memory
                officers_file.seek(0)
                zip_file.writestr(officers_filename, officers_file.read())

                # Export data to separate Excel files for each officer if related tables are selected
                if selected_related_tables:
                    for officer in selected_officers:
                        officer_data = []
                        row = {}
                        for field in selected_fields:
                            row[field] = getattr(officer, field)
                        officer_data.append(row)

                        # Create an in-memory Excel file for the current officer
                        officer_file = BytesIO()
                        officer_filename = (
                            f"{officer.birth_name.replace(' ', '_')}.xlsx"
                        )

                        with pd.ExcelWriter(
                            officer_file, engine="openpyxl"
                        ) as writer:
                            # Write general officer info to "Officers" sheet
                            field_labels = [
                                GENERAL_INFO_FIELDS.get(field, field)
                                for field in selected_fields
                            ]
                            df_officer = pd.DataFrame(officer_data)
                            df_officer.columns = field_labels
                            df_officer.to_excel(
                                writer,
                                index=False,
                                sheet_name="Thông tin chung",
                            )

                            # Export related tables based on selection
                            for table_key in selected_related_tables:
                                sheet_config = SHEET_TO_MODEL_FIELDS.get(
                                    table_key
                                )
                                if sheet_config:
                                    export_related_data(
                                        writer=writer,
                                        officer=officer,
                                        sheet_config=sheet_config,
                                        sheet_name=table_key,
                                    )

                        # Ensure the Excel file is saved in memory
                        officer_file.seek(0)
                        zip_file.writestr(officer_filename, officer_file.read())

            # Prepare the response as a ZIP file
            in_memory_zip.seek(0)
            response = HttpResponse(
                in_memory_zip, content_type="application/zip"
            )
            response["Content-Disposition"] = (
                "attachment; filename=thong_tin_CB.zip"
            )
            return response

    # Redirect back if form is not valid or if method is GET
    return redirect("officer_list")


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
                            model = config.model
                            fields = config.fields
                            create_officer_related_objects(
                                request=request,
                                officer=officer,
                                file=file,
                                sheet_name=sheet_name,
                                model=model,
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

    avatar = officer.images.filter(category="avatar").last()

    if request.method == "POST":
        form = f.OfficerInfoForm(request.POST, request.FILES, instance=officer)
        if form.is_valid():
            form.save()
            return redirect("officer_detail", pk=pk)
    else:
        form = f.OfficerInfoForm(instance=officer)

    return render(
        request, 
        "officers/officer_form.html", 
        {"form": form, "avatar": avatar}  # Pass the avatar to the template
    )


@login_required
def officer_detail(request, pk):
    officer = get_object_or_404(m.Officer, pk=pk)
    disciplines = officer.disciplines.all()

    # Fetch the avatar for the officer (filter by category "avatar")
    avatar = officer.images.filter(category="avatar").last()

    context = {
        "officer": officer,
        "disciplines": disciplines,
        "avatar": avatar,  # Pass the avatar object to the template
    }
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
        return super().get_success_url()


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

        try:
            singular_field = self.get_singular_field_name(
                self.related_context_field
            )
            context[f"edit_{singular_field}_id"] = self.object.id
        except AttributeError:
            pass

        return context

    def get_singular_field_name(self, field_name):
        """
        Converts plural field names to singular.
        """
        if field_name.endswith("ves"):
            return field_name[:-1]
        elif field_name.endswith("les"):
            return field_name[:-1]
        elif field_name.endswith("nes"):
            return field_name[:-1]
        elif field_name.endswith("ies"):
            return field_name[:-3] + "y"
        elif field_name.endswith("es"):
            return field_name[:-2]
        elif field_name.endswith("s"):
            return field_name[:-1]
        return field_name


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
    template_name = "officers/officer_title_manage.html"
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
    template_name = "officers/position_plan_manage.html"
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
    template_name = "officers/learning_path_manage.html"
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
    template_name = "officers/work_process_manage.html"
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
    template_name = "officers/salary_process_manage.html"
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
    template_name = "officers/laudatory_manage.html"
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
class LaudatoryUpdateView(PermissionRequiredMixin, LaudatoryMixin, UpdateView):
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
    template_name = "officers/discipline_manage.html"
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
    template_name = "officers/relative_manage.html"
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
class RelativeUpdateView(PermissionRequiredMixin, RelativeMixin, UpdateView):
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
    template_name = "officers/abroad_manage.html"
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
class AbroadUpdateView(PermissionRequiredMixin, AbroadMixin, UpdateView):
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
    template_name = "officers/army_join_history_manage.html"
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
    template_name = "officers/health_manage.html"
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
class HealthUpdateView(PermissionRequiredMixin, HealthMixin, UpdateView):
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


########################################################
# Officer Images


# List View
class ImageListView(LoginRequiredMixin, ListView):
    model = m.Image
    template_name = "officers/image_list.html"
    context_object_name = "images"
    pk_url_kwarg = "pk"  # Officer's pk

    def get_queryset(self):
        # Retrieve the officer and filter images for the specific officer
        self.officer = get_object_or_404(
            m.Officer, pk=self.kwargs[self.pk_url_kwarg]
        )
        queryset = self.officer.images.all()

        # Filter images by category if specified in query parameters
        category = self.request.GET.get("category")
        if category in dict(IMAGES_CATEGORY):
            queryset = queryset.filter(category=category)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["officer"] = self.officer
        context["category_labels"] = {
            choice[0]: choice[1] for choice in IMAGES_CATEGORY
        }
        return context


# Create Image View
class ImageCreateView(LoginRequiredMixin, View):
    form_class = f.ImageForm
    template_name = "officers/image_upload.html"  # Use the new upload template

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        officer = get_object_or_404(m.Officer, pk=self.kwargs["pk"])
        return render(request, self.template_name, {"form": form, "officer": officer})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        officer = get_object_or_404(m.Officer, pk=self.kwargs["pk"])

        if form.is_valid():
            category = form.cleaned_data["category"]
            description = form.cleaned_data["description"]
            images = request.FILES.getlist("image")  # Get list of uploaded files

            for image_file in images:
                m.Image.objects.create(
                    officer=officer,
                    image=image_file,
                    description=description,
                    category=category
                )

            return redirect("url_image", pk=officer.pk)

        return render(request, self.template_name, {"form": form, "officer": officer})

# Update Image View
class ImageUpdateView(LoginRequiredMixin, UpdateView):
    model = m.Image
    form_class = f.ImageForm
    template_name = "officers/image_update.html"  # Use the new update template
    pk_url_kwarg = 'image_pk'
    context_object_name = 'image'

    def get_object(self):
        # Ensure the image belongs to the correct officer
        officer = get_object_or_404(m.Officer, pk=self.kwargs["officer_pk"])
        return get_object_or_404(m.Image, pk=self.kwargs["image_pk"], officer=officer)
    
    def get_success_url(self):
        return reverse_lazy(
            "url_image", kwargs={"pk": self.kwargs["officer_pk"]}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["officer"] = self.get_object().officer
        return context


# Delete Image View
class ImageDeleteView(LoginRequiredMixin, DeleteView):
    model = m.Image
    template_name = "officers/image_confirm_delete.html"
    pk_url_kwarg = "image_pk"  # Image's pk
    officer_url_kwarg = "officer_pk"  # Officer's pk

    def get_object(self):
        officer = get_object_or_404(
            m.Officer, pk=self.kwargs[self.officer_url_kwarg]
        )
        return get_object_or_404(
            m.Image, pk=self.kwargs[self.pk_url_kwarg], officer=officer
        )

    def get_success_url(self):
        # Use pk instead of officer_pk to match the URL pattern
        return reverse_lazy(
            "url_image", kwargs={"pk": self.kwargs[self.officer_url_kwarg]}
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["officer"] = self.get_object().officer
        
        category = self.get_object().category
        context["category"] = dict(IMAGES_CATEGORY).get(category, category)

        return context


# Download selected images
def download_selected_images(request, officer_pk):
    if request.method == "POST":
        selected_image_ids = request.POST.getlist("selected_images")
        images = m.Image.objects.filter(
            pk__in=selected_image_ids, officer_id=officer_pk
        )

        # Create a ZIP file in memory
        response = HttpResponse(content_type="application/zip")
        zip_filename = f"officer_{officer_pk}_images.zip"
        response["Content-Disposition"] = (
            f'attachment; filename="{zip_filename}"'
        )

        with zipfile.ZipFile(response, "w") as zip_file:
            for image in images:
                image_path = image.image.path
                zip_file.write(image_path, os.path.basename(image_path))

        return response

    return redirect("url_image", pk=officer_pk)

def download_selected_pdfs(request, officer_pk):
    if request.method == "POST":
        selected_pdf_ids = request.POST.getlist("selected_pdfs")
        pdfs = m.PDF.objects.filter(
            pk__in=selected_pdf_ids, officer_id=officer_pk
        )

        # Create a ZIP file in memory
        response = HttpResponse(content_type="application/zip")
        zip_filename = f"officer_{officer_pk}_pdfs.zip"
        response["Content-Disposition"] = (
            f'attachment; filename="{zip_filename}"'
        )

        with zipfile.ZipFile(response, "w") as zip_file:
            for pdf in pdfs:
                pdf_path = pdf.pdf_file.path
                zip_file.write(pdf_path, os.path.basename(pdf_path))

        return response

def upload_pdf(request, officer_pk):
    officer = get_object_or_404(m.Officer, pk=officer_pk)
    if request.method == "POST":
        form = f.PDFForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_instance = form.save(commit=False)
            pdf_instance.officer = officer
            pdf_instance.save()
            return redirect("url_image", pk=officer_pk)
    else:
        form = f.PDFForm()

    return render(request, "officers/pdf_upload.html", {"form": form, "officer": officer})

class MediaListView(LoginRequiredMixin, ListView):
    template_name = "officers/image_list.html"  # Updated template name
    context_object_name = "media"  # Renamed for generic use
    pk_url_kwarg = "pk"  # Officer's pk

    def get_queryset(self):
        # Retrieve the officer
        self.officer = get_object_or_404(
            m.Officer, pk=self.kwargs[self.pk_url_kwarg]
        )

        # Fetch all images and PDFs for the officer
        images_queryset = self.officer.images.all()
        pdfs_queryset = self.officer.pdfs.all()

        # Filter by category if specified in query parameters
        category = self.request.GET.get("category")
        if category in dict(IMAGES_CATEGORY):
            images_queryset = images_queryset.filter(category=category)
            pdfs_queryset = pdfs_queryset.filter(category=category)

        # Combine both querysets into a list (return both as context)
        return {"images": images_queryset, "pdfs": pdfs_queryset}

    def get_context_data(self, **kwargs):
        # Get the default context
        context = super().get_context_data(**kwargs)

        # Add officer object to context
        context["officer"] = self.officer

        # Add category labels for filtering
        context["category_labels"] = {
            choice[0]: choice[1] for choice in IMAGES_CATEGORY
        }

        media = self.get_queryset()
        images = media["images"]
        pdfs = media["pdfs"]

        # Add separate images and PDFs to the context
        context["images"] = images
        context["pdfs"] = [{"pdf": pdf, "file_name": pdf.pdf_file.name.split("/")[-1]} for pdf in pdfs]

        return context

# Update PDF View
class PDFUpdateView(LoginRequiredMixin, UpdateView):
    model = m.PDF
    form_class = f.PDFForm
    template_name = "officers/pdf_update.html"  
    pk_url_kwarg = 'pdf_pk'
    context_object_name = 'pdf'

    def get_object(self):
        # Ensure the PDF belongs to the correct officer
        officer = get_object_or_404(m.Officer, pk=self.kwargs["officer_pk"])
        return get_object_or_404(m.PDF, pk=self.kwargs["pdf_pk"], officer=officer)
    
    def get_success_url(self):
        return reverse_lazy(
            "url_image", kwargs={"pk": self.kwargs["officer_pk"]}
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["officer"] = self.get_object().officer
        context["file_name"] = self.get_object().pdf_file.name.split("/")[-1]
        return context
    
# Delete PDF View
class PDFDeleteView(LoginRequiredMixin, DeleteView):
    model = m.PDF
    template_name = "officers/pdf_confirm_delete.html"
    pk_url_kwarg = "pdf_pk"  # PDF's pk
    officer_url_kwarg = "officer_pk"  # Officer's pk

    def get_object(self):
        officer = get_object_or_404(
            m.Officer, pk=self.kwargs[self.officer_url_kwarg]
        )
        return get_object_or_404(
            m.PDF, pk=self.kwargs[self.pk_url_kwarg], officer=officer
        )

    def get_success_url(self):
        # Use pk instead of officer_pk to match the URL pattern
        return reverse_lazy(
            "url_image", kwargs={"pk": self.kwargs[self.officer_url_kwarg]}
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["file_name"] = self.get_object().pdf_file.name.split("/")[-1]
        category = self.get_object().category
        context["category"] = dict(IMAGES_CATEGORY).get(category, category)
        
        context["officer"] = self.get_object().officer
        
        return context