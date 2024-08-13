from django import forms

from .models import Officer


class OfficerInfoForm(forms.ModelForm):
    class Meta:
        model = Officer
        fields = ["name", "date_of_birth", "address", "id_ca"]
