import unicodedata
from datetime import datetime

import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from officers.constants import GENERAL_INFO_FIELDS

from .forms import ExcelUploadForm, OfficerExportForm, OfficerInfoForm
from .models import Officer, PositionPlan, Title


def extract_officer_data(
    index, row, fields_dict, required_fields, date_fields
):  # noqa
    officer_data = {}
    row_missing_fields = {"row": index + 1, "missing_fields": []}
    skip_row = False

    for field, column in fields_dict.items():
        if field in date_fields:
            officer_data[field] = get_day(row, column)
        else:
            officer_data[field] = row.get(column, "")

        # Add the empty fields to the missing_fields list
        if (
            not officer_data[field]
            or officer_data[field] == "nan"
            or pd.isna(officer_data[field])
        ):
            row_missing_fields["missing_fields"].append(field)

            # If the field is required and empty, skip this row
            if field in required_fields:
                skip_row = True

    return officer_data, row_missing_fields, skip_row


def get_day(row, column):
    default_date = datetime(1800, 1, 1)
    try:
        day = row.get(column, None)
        # print(f"Raw value for day: {day}, Type: {type(day)}")

        if pd.isna(day):  # Check for NaT or NaN values
            return default_date

        if isinstance(day, str):
            # Handle string dates
            date_time = datetime.strptime(day, "%d/%m/%Y")
        elif isinstance(day, pd.Timestamp):
            # If it's a pandas Timestamp, we can convert it directly
            date_time = day.to_pydatetime()
        elif isinstance(day, datetime):
            # If it's already a datetime object, just return it
            date_time = day
        else:
            return default_date

        return date_time
    except ValueError:
        print(f"Failed to parse date for {row['birth_name']} with value: {day}")
        return default_date


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

    officers = Officer.objects.all()  # Start with all officers

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
                None, Officer.objects.values_list(field, flat=True).distinct()
            )
        )

    context["officers"] = officers
    context["query"] = query
    context["id_ca_query"] = id_ca_query
    context["selected_year_of_birth"] = selected_year_of_birth

    # Handle export functionality
    if request.method == "POST" and "export" in request.POST:
        form = OfficerExportForm(request.POST)
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
        form = OfficerExportForm(initial={"officers": officers})

    context["form"] = form
    return render(request, "officers/officer_list.html", context)


@login_required
@permission_required("officers.add_officer", raise_exception=True)
def officer_create(request):
    if request.method == "POST":
        form = OfficerInfoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("officer_list")
    else:
        form = OfficerInfoForm()

    return render(request, "officers/officer_form.html", {"form": form})


@login_required
@permission_required("officers.add_officer", raise_exception=True)
def excel_upload(request):
    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist("files")
            print(len(files))
            for file in files:
                try:
                    data = pd.read_excel(file, "Thông tin chung")

                    # Add required fields here
                    required_fields = ["birth_name", "id_ca"]
                    date_fields = [
                        "date_of_birth",
                        "date_update",
                    ]

                    # Iterate over the rows and create Officer objects
                    for index, row in data.iterrows():
                        officer_data, row_missing_fields, skip_row = (
                            extract_officer_data(
                                index,
                                row,
                                GENERAL_INFO_FIELDS,
                                required_fields,
                                date_fields,
                            )
                        )

                        if skip_row:
                            messages.warning(
                                request,
                                f"Skipping row {row_missing_fields['row']} due to missing fields: {', '.join(row_missing_fields['missing_fields'])}",  # noqa
                            )
                            continue

                        try:
                            officer = Officer.objects.create(**officer_data)
                        except IntegrityError as e:
                            # Check for specific IntegrityError messages
                            if "officers_officer.id_ca" in str(e):
                                messages.warning(
                                    request,
                                    f"Skipping row {index + 1} due to duplicate with existing officer '{officer_data['birth_name']}' with ID '{officer_data['id_ca']}'",  # noqa
                                )
                            else:
                                # Log or handle unexpected IntegrityError differently
                                messages.error(
                                    request,
                                    f"Error processing row {index + 1}: {str(e)}",
                                )
                            continue  # Skip to the next row

                        title_df = pd.read_excel(file, "Chức danh")
                        for _, title_row in title_df.iterrows():
                            appointed_date = get_day(title_row, "Ngày bổ nhiệm")
                            title = title_row.get("Chức danh", "")
                            try:
                                Title.objects.create(
                                    officer=officer,
                                    appointed_date=appointed_date,
                                    title=title,
                                )
                            except IntegrityError as e:
                                messages.error(
                                    request,
                                    f"Error processing title for officer {officer.birth_name}: {e}",
                                )
                        
                        position_plan_df = pd.read_excel(file, "Quy hoạch")
                        for _, position_plan_row in position_plan_df.iterrows():
                            period = position_plan_row.get("Giai đoạn", "")
                            position = position_plan_row.get("Quy hoạch", "")
                            try:
                                PositionPlan.objects.create(
                                    officer=officer,
                                    period=period,
                                    position=position,
                                )
                            except IntegrityError as e:
                                messages.error(
                                    request,
                                    f"Error processing position plan for officer {officer.birth_name}: {e}",
                                )
                except Exception as e:
                    messages.error(
                        request, f"Error processing file {file.name}: {e}"
                    )
            return redirect("officer_list")
    else:
        form = ExcelUploadForm()

    return render(request, "officers/excel_upload_form.html", {"form": form})


@login_required
@permission_required("officers.change_officer", raise_exception=True)
def officer_update(request, pk):
    officer = get_object_or_404(Officer, pk=pk)

    if request.method == "POST":
        form = OfficerInfoForm(request.POST, instance=officer)
        if form.is_valid():
            form.save()
            return redirect("officer_list")
    else:
        form = OfficerInfoForm(instance=officer)

    return render(request, "officers/officer_form.html", {"form": form})


@login_required
def officer_detail(request, pk):
    officer = get_object_or_404(Officer, pk=pk)
    return render(
        request, "officers/officer_detail.html", {"officer": officer}
    )  # noqa


@login_required
@permission_required("officers.delete_officer", raise_exception=True)
def officer_delete(request, pk):
    officer = get_object_or_404(Officer, pk=pk)
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
        Officer.objects.all().delete()
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
    officer = get_object_or_404(Officer, pk=pk)
    titles = officer.titles.all()
    context = {"officer": officer, "titles": titles}
    return render(request, "officers/officer_title.html", context)


@login_required
def officer_position_plan(request, pk):
    officer = get_object_or_404(Officer, pk=pk)
    position_plans = officer.position_plans.all()
    context = {"officer": officer, "position_plans": position_plans}
    return render(request, "officers/officer_position_plan.html", context)
