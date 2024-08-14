import pandas as pd
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ExcelUploadForm, OfficerInfoForm
from .models import Officer


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
                    date_of_birth=(
                        pd.to_datetime(
                            row.get("date_of_birth", None), errors="coerce"
                        ).date()
                        if row.get("date_of_birth")
                        else None
                    ),
                    address=row.get("address", ""),
                    id_ca=row.get("id_ca", ""),
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
