from datetime import datetime

from django import forms

from officers.classes import RelatedBaseForm
from officers.config import SHEET_TO_MODEL_FIELDS

from . import constants as c
from . import models as m


class OfficerInfoForm(forms.ModelForm):
    class Meta:
        model = m.Officer
        fields = [key for key in c.GENERAL_INFO_FIELDS.keys()]
        fields += [key for key in c.GENERAL_INFO_ADDED_FIELDS.keys()]
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
        for key, value in c.GENERAL_INFO_FIELDS.items():
            self.fields[key].label = value
        for key, value in c.GENERAL_INFO_ADDED_FIELDS.items():
            self.fields[key].label = value

        # add placeholders for GENERAL_INFO_DATE_FIELDS
        for field in c.GENERAL_INFO_MONTH_FIELDS:
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
        for field in c.GENERAL_INFO_MONTH_FIELDS:
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
        required=True,
    )


class OfficerExportForm(forms.Form):
    officers = forms.ModelMultipleChoiceField(
        queryset=m.Officer.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    fields = forms.MultipleChoiceField(
        choices=[],  # Initialize with an empty list; choices will be set dynamically
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    related_tables = forms.MultipleChoiceField(
        choices=[],  # This will hold the related table choices
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get the field choices dynamically with labels from OfficerInfoForm
        self.fields["fields"].choices = self.get_field_choices()

        # Get the related table choices
        self.fields["related_tables"].choices = self.get_related_table_choices()

    def get_field_choices(self):
        # Map the fields from Officer model to their corresponding labels in OfficerInfoForm
        form = (
            OfficerInfoForm()
        )  # Initialize OfficerInfoForm to access its fields
        field_choices = []

        for field_name in m.Officer._meta.fields:
            # Get the field's label from OfficerInfoForm if available
            label = (
                form.fields[field_name.name].label
                if field_name.name in form.fields
                else field_name.verbose_name
            )
            field_choices.append((field_name.name, label))

        return field_choices
    
    def get_related_table_choices(self):
        """
        Get the related table choices from the SHEET_TO_MODEL_FIELDS config.
        """
        related_table_choices = []
        for key, _ in SHEET_TO_MODEL_FIELDS.items():
            # Use the key (which is the display name) for the related tables
            related_table_choices.append((key, key))
        
        return related_table_choices


class TitleForm(RelatedBaseForm):
    class Meta:
        model = m.Title
        field_config = c.TITLE_FIELDS
        fields = list(field_config.keys())

class PositionPlanForm(RelatedBaseForm):
    class Meta:
        model = m.PositionPlan
        field_config = c.POSITION_PLAN_FIELDS
        fields = list(field_config.keys())

class LearningPathForm(RelatedBaseForm):
    class Meta:
        model = m.LearningPath
        field_config = c.LEARNING_PATH_FIELDS
        fields = list(field_config.keys())

class WorkProcessForm(RelatedBaseForm):
    class Meta:
        model = m.WorkProcess
        field_config = c.WORK_PROCESS_FIELDS
        fields = list(field_config.keys())

class SalaryProcessForm(RelatedBaseForm):
    class Meta:
        model = m.SalaryProcess
        field_config = c.SALARY_PROCESS_FIELDS
        fields = list(field_config.keys())

class LaudatoryForm(RelatedBaseForm):
    class Meta:
        model = m.Laudatory
        field_config = c.LAUDATORY_FIELDS
        fields = list(field_config.keys())

class DisciplineForm(RelatedBaseForm):
    class Meta:
        model = m.Discipline
        field_config = c.DISCIPLINE_FIELDS
        fields = list(field_config.keys())

class RelativeForm(RelatedBaseForm):
    class Meta:
        model = m.Relative
        field_config = c.RELATIVE_FIELDS
        fields = list(field_config.keys())

class AbroadForm(RelatedBaseForm):
    class Meta:
        model = m.Abroad
        field_config = c.ABROAD_FIELDS
        fields = list(field_config.keys())

class ArmyJoinHistoryForm(RelatedBaseForm):
    class Meta:
        model = m.ArmyJoinHistory
        field_config = c.ARMY_JOIN_HISTORY_FIELDS
        fields = list(field_config.keys())

class HealthForm(RelatedBaseForm):
    class Meta:
        model = m.Health
        field_config = c.HEALTH_FIELDS
        fields = list(field_config.keys())