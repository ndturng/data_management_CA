from datetime import datetime

import pandas as pd
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

            # Iterate over the rows and create Officer objects
            for _, row in data.iterrows():
                Officer.objects.create(
                    name=row.get("Họ và tên", ""),
                    date_of_birth=get_day(row, "Ngày,tháng, năm sinh"),
                    birth_year=get_day(row, "Ngày,tháng, năm sinh").year,
                    current_residence=(
                        str(row.get("Chổ ở hiện nay: Thôn ( Khu Phố)", ""))
                        + ", "
                        + str(row.get("Xã (Phường)", ""))
                        + ", "
                        + str(row.get("Huyện (Thành Phố)", ""))
                        + ", "
                        + str(row.get("Tỉnh", ""))
                    ),
                    id_ca=row.get("Số hiệu", ""),
                    id_citizen=str(row.get("Số CMND", "")).split(".")[0],
                    gender=row.get("Giới tính", ""),
                    date_of_enlistment=get_day(row, "Vào ngành"),
                    enlistment_year=get_day(row, "Vào ngành").year,
                    date_join_party=get_day(row, "Vào đảng"),
                    join_party_year=get_day(row, "Vào đảng").year,
                    home_town=row.get("Quê quán", ""),
                    blood_type=row.get("Nhóm Máu", ""),
                    education=row.get("Trình độ", ""),
                    certi_of_IT=row.get("Tin học", ""),
                    certi_of_foreign_language=row.get("Ngoại Ngữ", ""),
                    political_theory=row.get("Trình độ LLCT", ""),
                    military_rank=row.get("Cấp bậc hàm", ""),
                    rank_type=row.get("Loại hàm", ""),
                    position=row.get("Chức vụ", ""),
                    work_unit=row.get(
                        "Vị trí công tác", ""
                    ),  # noqa # Đơn vị công tác
                    military_type=row.get("Lực lượng", ""),
                    equipment_type=row.get("Quân trang", ""),
                    size_of_shoes=row.get("Giày", ""),
                    size_of_hat=row.get("Mũ", ""),
                    size_of_clothes=str(row.get("Quần áo", "")).split(".")[0],
                    bank_account_BIDV=row.get("Số tài khoản BIDV", ""),
                    phone_number=str(row.get("Số Điện thoại", "")).split(".")[
                        0
                    ],  # noqa
                    laudatory=row.get("Khen thưởng", ""),
                    punishment=row.get("Kỷ luật", ""),
                )
            return redirect(
                "officer_list"
            )  # Replace with your actual list view name
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
    )


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
