from datetime import datetime

import pandas as pd
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db.models.functions import ExtractYear

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
    officers = Officer.objects.all()

    # Search by name
    query = request.GET.get("q")
    if query:
        officers = Officer.objects.filter(name__icontains=query)

    # Filtering
    military_type = request.GET.get("military_type")
    military_rank = request.GET.get("military_rank")
    work_unit = request.GET.get("work_unit")
    blood_type = request.GET.get("blood_type")
    size_of_hat = request.GET.get("size_of_hat")
    political_theory = request.GET.get("political_theory")
    position = request.GET.get("position")
    year_of_birth = request.GET.get("year_of_birth")

    if military_type:
        officers = officers.filter(military_type=military_type)
    if military_rank:
        officers = officers.filter(military_rank=military_rank)
    if work_unit:
        officers = officers.filter(work_unit=work_unit)
    if blood_type:
        officers = officers.filter(blood_type=blood_type)
    if size_of_hat:
        officers = officers.filter(size_of_hat=size_of_hat)
    if political_theory:
        officers = officers.filter(political_theory=political_theory)
    if position:
        officers = officers.filter(position=position)
    if year_of_birth:
        officers = officers.filter(date_of_birth__year=year_of_birth)

    # Get unique sorted values for filter dropdowns
    military_types = sorted(
        filter(
            None,
            Officer.objects.values_list("military_type", flat=True).distinct(),
        )
    )
    military_ranks = sorted(
        filter(
            None,
            Officer.objects.values_list("military_rank", flat=True).distinct(),
        )
    )
    work_units = sorted(
        filter(
            None,
            Officer.objects.values_list("work_unit", flat=True).distinct(),
        )
    )
    blood_types = sorted(
        filter(
            None,
            Officer.objects.values_list("blood_type", flat=True).distinct(),
        )
    )
    political_theory = sorted(
        filter(
            None,
            Officer.objects.values_list("political_theory", flat=True).distinct(), # noqa
        )
    )
    hat_size = sorted(
        filter(
            None,
            Officer.objects.values_list("size_of_hat", flat=True).distinct(),
        )
    )
    position = sorted(
        filter(
            None, 
            Officer.objects.values_list("position", flat=True).distinct()
        )
    )
    years_of_birth = sorted(
        filter(
            None,
            Officer.objects.annotate(year_of_birth=ExtractYear("date_of_birth")) # noqa
            .values_list("year_of_birth", flat=True)
            .distinct()
        )
    )

    context = {
        "officers": officers,
        "military_types": military_types,
        "military_ranks": military_ranks,
        "work_units": work_units,
        "blood_types": blood_types,
        "hat_size": hat_size,
        "political_theory": political_theory,
        "position": position,
        "query": query,  # Pass the query back to the template
        "years_of_birth": years_of_birth,
    }
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
                    date_join_party=get_day(row, "Vào đảng"),
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
    return render(request, "officers/officer_detail.html", {"officer": officer}) # noqa


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