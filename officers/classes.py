from django import forms
from dataclasses import dataclass


@dataclass
class SheetConfig:
    model_class: type
    fields: dict


class RelatedBaseForm(forms.ModelForm):
    """
    Base form class to handle common behavior for all Officer-related forms.
    It dynamically applies field configurations from the Meta class of the derived form.
    """

    def __init__(self, *args, **kwargs):
        super(RelatedBaseForm, self).__init__(*args, **kwargs)
        
        # Fetch field configuration from the Meta class of the child form
        field_config = getattr(self.Meta, 'field_config', {})
        
        for field_name, label in field_config.items():
            self.fields[field_name].label = label
            self.fields[field_name].required = True
            
            # Set specific widgets and formats for certain fields
            if 'date' in field_name: 
                self.fields[field_name].input_formats = ["%d/%m/%Y"]
                self.fields[field_name].widget = forms.DateInput(
                    format="%d/%m/%Y",
                    attrs={"placeholder": "Ví dụ: 15/05/2025"}
                )
            elif "period" in field_name:
                self.fields[field_name].widget = forms.TextInput(
                    attrs={"placeholder": "Ví dụ: 2010 - 2015"}
                )
            elif "time" in field_name or "year" in field_name:
                self.fields[field_name].widget = forms.TextInput(
                    attrs={"placeholder": "Ví dụ: 2025"}
                )
            elif "coefficient" in field_name:
                self.fields[field_name].widget = forms.TextInput(
                    attrs={"placeholder": "Ví dụ: 5.4"}
                )
            elif "weight" in field_name:
                self.fields[field_name].widget = forms.TextInput(
                    attrs={"placeholder": "Ví dụ: 70"}
                )
            elif "height" in field_name:
                self.fields[field_name].widget = forms.TextInput(
                    attrs={"placeholder": "Ví dụ: 170"}
                )
            else:
                self.fields[field_name].widget = forms.TextInput(
                    attrs={"placeholder": f"Nhập {label.lower()}"}
                )