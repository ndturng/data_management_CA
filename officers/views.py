import pandas as pd
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ExcelUploadForm, OfficerInfoForm
from .models import Officer


def get_day(row, column):
    day = row.get(column, None)
    date_time = pd.to_datetime(day, errors="coerce").date()
    return date_time if day else None


def officer_list(request):
    officers = Officer.objects.all()
    return render(
        request, "officers/officer_list.html", {"officers": officers}
    )  # noqa


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


def excel_upload(request):
    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            data = pd.read_excel(file)

            # Iterate over the rows and create Officer objects
            for _, row in data.iterrows():
                Officer.objects.create(
                    name=row.get("name", ""),
                    date_of_birth=get_day(row, "date_of_birth"),
                    current_residence=row.get("current_residence", ""),
                    id_ca=row.get("id_ca", ""),
                    id_citizen=row.get("id_citizen", ""),
                    gender=row.get("gender", ""),
                    date_of_enlistment=get_day(row, "date_of_enlistment"),
                    date_join_party=get_day(row, "date_join_party"),
                    home_town=row.get("home_town", ""),
                    blood_type=row.get("blood_type", ""),
                    education=row.get("education", ""),
                    certi_of_IT=row.get("certi_of_IT", ""),
                    certi_of_foreign_language=row.get(
                        "certi_of_foreign_language", ""
                    ),
                    political_theory=row.get("political_theory", ""),
                    military_rank=row.get("military_rank", ""),
                    rank_type=row.get("rank_type", ""),
                    position=row.get("position", ""),
                    work_unit=row.get("work_unit", ""),
                    military_type=row.get("military_type", ""),
                    equipment_type=row.get("equipment_type", ""),
                    size_of_shoes=row.get("size_of_shoes", ""),
                    size_of_hat=row.get("size_of_hat", ""),
                    size_of_clothes=row.get("size_of_clothes", ""),
                    bank_account_BIDV=row.get("bank_account_BIDV", ""),
                    phone_number=row.get("phone_number", ""),
                    laudatory=row.get("laudatory", ""),
                    punishment=row.get("punishment", ""),
                )
            return redirect(
                "officer_list"
            )  # Replace with your actual list view name
    else:
        form = ExcelUploadForm()

    return render(request, "officers/excel_upload_form.html", {"form": form})


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


def officer_delete(request, pk):
    officer = get_object_or_404(Officer, pk=pk)
    if request.method == "POST":
        officer.delete()
        return redirect("officer_list")
    return render(
        request, "officers/officer_confirm_delete.html", {"officer": officer}
    )
