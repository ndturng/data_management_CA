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

    def __init__(self, *args, **kwargs):
        super(OfficerInfoForm, self).__init__(*args, **kwargs)
        # Set the labels for the fields
        for key, value in c.GENERAL_INFO_FIELDS.items():
            self.fields[key].label = value
        for key, value in c.GENERAL_INFO_ADDED_FIELDS.items():
            self.fields[key].label = value

        # add placeholders for GENERAL_INFO_DATE_FIELDS
        for field in c.GENERAL_INFO_MONTH_FIELDS:
            self.fields[field].widget.attrs["placeholder"] = "ví dụ: 06/2021"

        for field in c.GENERAL_INFO_DATE_FIELDS:
            self.fields[field].input_formats = ["%d/%m/%Y"]
            self.fields[field].widget = forms.DateInput(
                format="%d/%m/%Y", attrs={"placeholder": "ví dụ: 15/06/1990"}
            )

        if not self.initial.get("date_update"):
            self.initial["date_update"] = datetime.now().strftime("%d/%m/%Y")

    def clean_month_year(self, field_name):
        value = self.cleaned_data.get(field_name)
        if value:
            try:
                # Attempt to parse the date in MM/YYYY format
                datetime.strptime(value, "%m/%Y")
            except ValueError:
                # Raise a validation error if it doesn't match the expected format
                raise forms.ValidationError(
                    f"{self.fields[field_name].label}: nhập sai định dạng. Vui lòng nhập theo ví dụ: 06/2021"
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

    model_fields = forms.MultipleChoiceField(
        choices=[],  # Empty initially, choices will be set dynamically
        required=True,
    )

    related_tables = forms.MultipleChoiceField(
        choices=[],  # Empty initially, choices will be set dynamically
        required=False,
    )

    filter_options = forms.MultipleChoiceField(
        choices=[],  # Empty initially, choices will be set dynamically
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically load choices for the 'fields' field
        self.fields["model_fields"].choices = self.get_field_choices()

        # Dynamically load choices for the 'related_tables' field
        self.fields["related_tables"].choices = self.get_related_table_choices()

        # Dynamically load choices for the 'filter_options' field
        self.fields["filter_options"].choices = self.get_filter_options()

    def get_field_choices(self):
        """
        Dynamically generate choices for fields based on Officer model.
        """
        form = OfficerInfoForm()  # Initialize OfficerInfoForm to get field labels
        field_choices = []

        for field_name in m.Officer._meta.fields:
            if field_name.name == "id":
                continue  # Skip the 'id' field
            label = (
                form.fields[field_name.name].label
                if field_name.name in form.fields
                else field_name.verbose_name
            )
            value = field_name.name
            field_choices.append((value, label))

        return field_choices

    def get_related_table_choices(self):
        """
        Dynamically get related tables using the SHEET_TO_MODEL_FIELDS config.
        """
        related_table_choices = [
            (table_name, table_name)  
            for table_name, _ in SHEET_TO_MODEL_FIELDS.items()
        ]
        return related_table_choices

    def get_filter_options(self):
        """
        Dynamically generate filter options
        """
        filter_options = []
        # Loop through GENERAL_INFO_FIELDS
        for field_name, field_label in c.GENERAL_INFO_FIELDS.items():
            if field_name in (c.FILTER_FIELDS + c.SEARCH_FIELDS):
                filter_options.append((field_name, field_label))
        return filter_options


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


class ImageForm(forms.ModelForm):
    class Meta:
        model = m.Image
        fields = ["image", "description", "category"]  

        widgets = {
            "description": forms.TextInput(attrs={"class": "form-control rounded-lg w-full border-black"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control rounded-lg w-full border-black"}),
        }

    def __init__(self, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)
        self.fields["image"].label = "Tệp ảnh"
        self.fields["description"].label = "Mô tả"
        self.fields["category"].label = "Danh mục"

class PDFForm(forms.ModelForm):
    class Meta:
        model = m.PDF
        fields = ["pdf_file", "description", "category"]
        widgets = {
            "description": forms.TextInput(attrs={"class": "form-control rounded-lg w-full border-black"}),
            "pdf_file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control rounded-lg w-full border-black"}),
        }