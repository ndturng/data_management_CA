from datetime import datetime

from django import forms

from .constants import GENERAL_INFO_ADDED_FIELDS, GENERAL_INFO_DATE_FIELDS, GENERAL_INFO_FIELDS
from .models import Officer


class OfficerInfoForm(forms.ModelForm):
    class Meta:
        model = Officer
        fields = [key for key in GENERAL_INFO_FIELDS.keys()]
        fields += [key for key in GENERAL_INFO_ADDED_FIELDS.keys()]
        widgets = {
            "date_of_birth": forms.DateInput(
                format="%d-%m-%Y", attrs={"placeholder": "dd-mm-yyyy"}
            ),
            "date_update": forms.DateInput(
                format="%d-%m-%Y", attrs={"placeholder": "dd-mm-yyyy"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(OfficerInfoForm, self).__init__(*args, **kwargs)
        for key, value in GENERAL_INFO_FIELDS.items():
            self.fields[key].label = value
        for key, value in GENERAL_INFO_ADDED_FIELDS.items():
            self.fields[key].label = value
            
        # add placeholders for GENERAL_INFO_DATE_FIELDS
        for field in GENERAL_INFO_DATE_FIELDS:
            self.fields[field].widget.attrs["placeholder"] = "mm/yyyy"

        self.fields["date_of_birth"].input_formats = ["%d-%m-%Y"]
        if not self.initial.get("date_of_birth"):
            self.initial["date_of_birth"] = "01-01-1800"
            self.initial["birth_year"] = "1800"

        self.fields["date_update"].input_formats = ["%d-%m-%Y"]
        if not self.initial.get("date_update"):
            self.initial["date_update"] = datetime.now().strftime("%d-%m-%Y")

    def clean_month_year(self, field_name):
        value = self.cleaned_data.get(field_name)
        if value:
            try:
                # Attempt to parse the date in MM/YYYY format
                datetime.strptime(value, "%m/%Y")
            except ValueError:
                # Raise a validation error if it doesn't match the expected format
                raise forms.ValidationError(
                    f"{self.fields[field_name].label} must be in MM/YYYY format."
                )
        return value

    def clean(self):
        cleaned_data = super().clean()
        for field in GENERAL_INFO_DATE_FIELDS:
            cleaned_data[field] = self.clean_month_year(field)
        return cleaned_data

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result

class ExcelUploadForm(forms.Form):
    files = MultipleFileField(
        label="Select files",
        required=True,
        help_text="Select one or more Excel files to upload.",
    )

class OfficerExportForm(forms.Form):
    officers = forms.ModelMultipleChoiceField(
        queryset=Officer.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    fields = forms.MultipleChoiceField(
        choices=[],  # Initialize with an empty list; choices will be set dynamically
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get the field choices dynamically with labels from OfficerInfoForm
        self.fields["fields"].choices = self.get_field_choices()

    def get_field_choices(self):
        # Map the fields from Officer model to their corresponding labels in OfficerInfoForm
        form = OfficerInfoForm()  # Initialize OfficerInfoForm to access its fields
        field_choices = []

        for field_name in Officer._meta.fields:
            # Get the field's label from OfficerInfoForm if available
            label = (
                form.fields[field_name.name].label
                if field_name.name in form.fields
                else field_name.verbose_name
            )
            field_choices.append((field_name.name, label))

        return field_choices
