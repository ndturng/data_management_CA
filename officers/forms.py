from django import forms

from .models import Officer


class OfficerInfoForm(forms.ModelForm):
    class Meta:
        model = Officer
        fields = [
            "name",
            "date_of_birth",
            "id_ca",
            "id_citizen",
            "gender",
            "date_of_enlistment",
            "date_join_party",
            "home_town",
            "current_residence",
            "blood_type",
            "education",
            "certi_of_IT",
            "certi_of_foreign_language",
            "political_theory",
            "military_rank",
            "rank_type",
            "position",
            "work_unit",
            "military_type",
            "equipment_type",
            "size_of_shoes",
            "size_of_hat",
            "size_of_clothes",
            "bank_account_BIDV",
            "phone_number",
            "laudatory",
            "punishment",
        ]


class ExcelUploadForm(forms.Form):
    file = forms.FileField(label="Upload Excel file")
