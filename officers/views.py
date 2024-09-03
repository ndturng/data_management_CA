from datetime import datetime

import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ExcelUploadForm, OfficerInfoForm
from .models import Officer


def get_day(row, column):
    try:
        day = row.get(column, None)
        # print(f"Raw value for day: {day}, Type: {type(day)}")

        if pd.isna(day):  # Check for NaT or NaN values
            return None

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
            return None

        return date_time
    except ValueError:
        print(f"Failed to parse date for {row['name']} with value: {day}")
        return None


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
        "year_enlistment": "enlistment_year",
        "education": "education",
        "current_residence": "current_residence",
        "home_town": "home_town",
    }
    officers = Officer.objects.all()  # Start with all officers

    # Search by name
    query = request.GET.get("q")
    if query:
        officers = Officer.objects.filter(name__icontains=query)

    # Loop through each field in the filter_fields dictionary
    for field, filter_action in filter_fields.items():
        # Get the value from the request GET parameters
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
        if field == "year_enlistment":
            selected_year_enlistment = int(value) if value else None
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
        "years_enlistment": "enlistment_year",
        "home_towns": "home_town",
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
    context["selected_year_of_birth"] = selected_year_of_birth
    context["selected_year_enlistment"] = selected_year_enlistment

    return render(request, "officers/officer_list.html", context)


@login_required
@permission_required("officers.add_officer", raise_exception=True)
def officer_create(request):
    if request.method == "POST":
        form = OfficerInfoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(
                "officer_list"
            )  # Replace with your actual list view name
    else:
        form = OfficerInfoForm()

    return render(request, "officers/officer_form.html", {"form": form})


@login_required
@permission_required("officers.add_officer", raise_exception=True)
def excel_upload(request):
    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            data = pd.read_excel(file)

            fields_dict = {
                "name": "Họ và tên",
                "date_of_birth": "Ngày,tháng, năm sinh",
                "birth_year": "Ngày,tháng, năm sinh",
                "khu_pho": "Chổ ở hiện nay: Thôn ( Khu Phố)",
                "phuong": "Xã (Phường)",
                "huyen": "Huyện (Thành Phố)",
                "tinh": "Tỉnh",
                "id_ca": "Số hiệu",
                "id_citizen": "Số CMND",
                "gender": "Giới tính",
                "date_of_enlistment": "Vào ngành",
                "date_join_party": "Vào đảng",
                "home_town": "Quê quán",
                "blood_type": "Nhóm Máu",
                "education": "Trình độ",
                "certi_of_IT": "Tin học",
                "certi_of_foreign_language": "Ngoại Ngữ",
                "political_theory": "Trình độ LLCT",
                "military_rank": "Cấp bậc hàm",
                "rank_type": "Loại hàm",
                "position": "Chức vụ",
                "work_unit": "Vị trí công tác",
                "military_type": "Lực lượng",
                "equipment_type": "Quân trang",
                "size_of_shoes": "Giày",
                "size_of_hat": "Mũ",
                "size_of_clothes": "Quần áo",
                "bank_account_BIDV": "Số tài khoản BIDV",
                "phone_number": "Số Điện thoại",
                "laudatory": "Khen thưởng",
                "punishment": "Kỷ luật",
            }

            # Add required fields here
            required_fields = ["name", "id_ca"]
            date_fields = ["date_of_birth", "date_of_enlistment", "date_join_party"] # noqa

            # Iterate over the rows and create Officer objects
            for index, row in data.iterrows():
                skip_row = False
                officer_data = {}
                row_missing_fields = {"row": index + 1, "missing_fields": []}

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
                    ):  # noqa
                        row_missing_fields["missing_fields"].append(field)

                        # If the field is required and empty, skip this row
                        if field in required_fields:
                            skip_row = True

                if skip_row:
                    messages.warning(
                        request,
                        f"Skipping row {row_missing_fields['row']} due to missing fields: {', '.join(row_missing_fields['missing_fields'])}",  # noqa
                    )
                    continue

                Officer.objects.create(  # implement a shorter way to create an object # noqa
                    name=officer_data["name"],
                    date_of_birth=officer_data["date_of_birth"],
                    birth_year=officer_data["date_of_birth"].year,
                    current_residence=(
                        str(officer_data["khu_pho"])
                        + ", "
                        + str(officer_data["phuong"])
                        + ", "
                        + str(officer_data["huyen"])
                        + ", "
                        + str(officer_data["tinh"])
                    ),
                    id_ca=officer_data["id_ca"],
                    id_citizen=officer_data["id_citizen"],
                    gender=officer_data["gender"],
                    date_of_enlistment=officer_data["date_of_enlistment"],
                    enlistment_year=officer_data[
                        "date_of_enlistment"
                    ].year,  # noqa
                    date_join_party=officer_data["date_join_party"],
                    join_party_year=officer_data["date_join_party"].year,
                    home_town=officer_data["home_town"],
                    blood_type=officer_data["blood_type"],
                    education=officer_data["education"],
                    certi_of_IT=officer_data["certi_of_IT"],
                    certi_of_foreign_language=officer_data[
                        "certi_of_foreign_language"
                    ],
                    political_theory=officer_data["political_theory"],
                    military_rank=officer_data["military_rank"],
                    rank_type=officer_data["rank_type"],
                    position=officer_data["position"],
                    work_unit=officer_data["work_unit"],
                    military_type=officer_data["military_type"],
                    equipment_type=officer_data["equipment_type"],
                    size_of_shoes=officer_data["size_of_shoes"],
                    size_of_hat=officer_data["size_of_hat"],
                    size_of_clothes=str(officer_data["size_of_clothes"]).split(
                        "."
                    )[
                        0
                    ],  # noqa
                    bank_account_BIDV=officer_data["bank_account_BIDV"],
                    phone_number=str(officer_data["phone_number"]).split(".")[
                        0
                    ],  # noqa
                    laudatory=officer_data["laudatory"],
                    punishment=officer_data["punishment"],
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
