import unicodedata

import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

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


@login_required
def officer_title(request, pk):
    officer = get_object_or_404(m.Officer, pk=pk)
    titles = officer.titles.all()

    context = {
        "officer": officer,
        "titles": titles,
    }

    return render(request, "officers/officer_title.html", context)


@login_required
@permission_required("officers.adjust_officer_title", raise_exception=True)
def officer_title_manage(request, pk, title_id=None):
    officer = get_object_or_404(m.Officer, pk=pk)
    titles = officer.titles.all()
    # If title_id is provided, editing an existing title
    if title_id:
        title = get_object_or_404(m.Title, id=title_id, officer=officer)
        form = f.TitleForm(instance=title)
    else:
        title = None
        form = f.TitleForm()

    if request.method == "POST":
        if title:
            form = f.TitleForm(request.POST, instance=title)
        else:
            form = f.TitleForm(request.POST)

        if form.is_valid():
            new_title = form.save(commit=False)
            new_title.officer = officer  # Link the title to the officer
            new_title.save()
            return redirect("officer_title_view", pk=officer.pk)

    context = {
        "officer": officer,
        "form": form,
        "titles": titles,
        "edit_title_id": title_id,
    }

    return render(request, "officers/officer_title_manage.html", context)


@login_required
@permission_required("officers.delete_officer_title", raise_exception=True)
def delete_title(request, pk, title_id):
    officer = get_object_or_404(m.Officer, pk=pk)
    title = get_object_or_404(m.Title, id=title_id, officer=officer)

    if request.method == "POST":
        title.delete()
        return redirect("officer_title_view", pk=officer.pk)

    return render(
        request,
        "officers/confirm_delete.html",
        {"officer": officer, "title": title},
    )


@login_required
def officer_position_plan(request, pk):
    officer = get_object_or_404(m.Officer, pk=pk)
    position_plans = officer.position_plans.all()
    context = {"officer": officer, "position_plans": position_plans}
    return render(request, "officers/officer_position_plan.html", context)


@login_required
def officer_learning_path(request, pk):
    officer = get_object_or_404(m.Officer, pk=pk)
    learning_paths = officer.learning_paths.all()
    context = {"officer": officer, "learning_paths": learning_paths}
    return render(request, "officers/officer_learning_path.html", context)


@login_required
def officer_work_process(request, pk):
    officer = get_object_or_404(m.Officer, pk=pk)
    work_processes = officer.work_processes.all()
    context = {"officer": officer, "work_processes": work_processes}
    return render(request, "officers/officer_work_process.html", context)


@login_required
def officer_salary_process(request, pk):
    officer = get_object_or_404(m.Officer, pk=pk)
    salary_processes = officer.salary_processes.all()
    context = {"officer": officer, "salary_processes": salary_processes}
    return render(request, "officers/officer_salary_process.html", context)


@login_required
def officer_laudatory(request, pk):
    officer = get_object_or_404(m.Officer, pk=pk)
    laudatories = officer.laudatories.all()
    context = {"officer": officer, "laudatories": laudatories}
    return render(request, "officers/officer_laudatory.html", context)


@login_required
def officer_discipline(request, pk):
    officer = get_object_or_404(m.Officer, pk=pk)
    disciplines = officer.disciplines.all()
    context = {"officer": officer, "disciplines": disciplines}
    return render(request, "officers/officer_discipline.html", context)


@login_required
def officer_relative(request, pk):
    officer = get_object_or_404(m.Officer, pk=pk)
    relatives = officer.relatives.all()
    context = {"officer": officer, "relatives": relatives}
    return render(request, "officers/officer_relative.html", context)


@login_required
def officer_abroad(request, pk):
    officer = get_object_or_404(m.Officer, pk=pk)
    abroads = officer.abroads.all()
    context = {"officer": officer, "abroads": abroads}
    return render(request, "officers/officer_abroad.html", context)


@login_required
def officer_army_join_history(request, pk):
    officer = get_object_or_404(m.Officer, pk=pk)
    army_join_histories = officer.army_join_histories.all()
    context = {"officer": officer, "army_join_histories": army_join_histories}
    return render(request, "officers/officer_army_join_history.html", context)


@login_required
def officer_health(request, pk):
    officer = get_object_or_404(m.Officer, pk=pk)
    healths = officer.healths.all()
    context = {"officer": officer, "healths": healths}
    return render(request, "officers/officer_health.html", context)
