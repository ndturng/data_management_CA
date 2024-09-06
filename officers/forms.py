from django import forms

from .models import Officer


class OfficerInfoForm(forms.ModelForm):
    class Meta:
        model = Officer
        fields = [
            "name",
            "date_of_birth",
            "birth_year",
            "id_ca",
            "id_citizen",
            "gender",
            "date_of_enlistment",
            "enlistment_year",
            "date_join_party",
            "join_party_year",
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
        widgets = {
            "date_of_birth": forms.DateInput(
                format="%d-%m-%Y", attrs={"placeholder": "dd-mm-yyyy"}
            ),
            "date_of_enlistment": forms.DateInput(
                format="%d-%m-%Y", attrs={"placeholder": "dd-mm-yyyy"}
            ),
            "date_join_party": forms.DateInput(
                format="%d-%m-%Y", attrs={"placeholder": "dd-mm-yyyy"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(OfficerInfoForm, self).__init__(*args, **kwargs)
        self.fields["name"].label = "Họ và tên"

        self.fields["date_of_birth"].label = "Ngày sinh"
        self.fields["date_of_birth"].input_formats = ["%d-%m-%Y"]
        if not self.initial.get("date_of_birth"):
            self.initial["date_of_birth"] = "01-01-1800"
            self.initial["birth_year"] = "1800"

        self.fields["date_of_enlistment"].label = "Ngày vào ngành"
        self.fields["date_of_enlistment"].input_formats = ["%d-%m-%Y"]
        if not self.initial.get("date_of_enlistment"):
            self.initial["date_of_enlistment"] = "01-01-1800"
            self.initial["enlistment_year"] = "1800"

        self.fields["date_join_party"].label = "Ngày vào Đảng"
        self.fields["date_join_party"].input_formats = ["%d-%m-%Y"]
        if not self.initial.get("date_join_party"):
            self.initial["date_join_party"] = "01-01-1800"
            self.initial["join_party_year"] = "1800"

        self.fields["id_ca"].label = "Số hiệu"
        self.fields["id_citizen"].label = "Số CMND"
        self.fields["gender"].label = "Giới tính"
        self.fields["home_town"].label = "Quê quán"
        self.fields["current_residence"].label = "Chổ ở hiện nay"
        self.fields["blood_type"].label = "Nhóm máu"
        self.fields["education"].label = "Trình độ"
        self.fields["certi_of_IT"].label = "Chứng chỉ tin học"
        self.fields["certi_of_foreign_language"].label = "Chứng chỉ ngoại ngữ"
        self.fields["political_theory"].label = "Trình độ LLCT"
        self.fields["military_rank"].label = "Cấp bậc hàm"
        self.fields["rank_type"].label = "Loại hàm"
        self.fields["position"].label = "Chức vụ"
        if not self.initial.get("position"):
            self.initial["position"] = "nan"
        self.fields["work_unit"].label = "Đơn vị công tác"
        self.fields["military_type"].label = "Lực lượng"
        self.fields["equipment_type"].label = "Quân trang"
        self.fields["size_of_shoes"].label = "Size giày"
        self.fields["size_of_hat"].label = "Size mũ"
        self.fields["size_of_clothes"].label = "Size quần áo"
        self.fields["bank_account_BIDV"].label = "Số tài khoản BIDV"
        self.fields["phone_number"].label = "Số điện thoại"
        self.fields["laudatory"].label = "Khen thưởng"
        self.fields["punishment"].label = "Kỷ luật"


class ExcelUploadForm(forms.Form):
    file = forms.FileField(label="Upload Excel file")


class OfficerExportForm(forms.Form):
    officers = forms.ModelMultipleChoiceField(
        queryset=Officer.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    fields = forms.MultipleChoiceField(
        choices=[],  # Initialize with an empty list; choices will be set dynamically
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get the field choices dynamically with labels from OfficerInfoForm
        self.fields['fields'].choices = self.get_field_choices()

    def get_field_choices(self):
        # Map the fields from Officer model to their corresponding labels in OfficerInfoForm
        form = OfficerInfoForm()  # Initialize OfficerInfoForm to access its fields
        field_choices = []

        for field_name in Officer._meta.fields:
            # Get the field's label from OfficerInfoForm if available
            label = form.fields[field_name.name].label if field_name.name in form.fields else field_name.verbose_name
            field_choices.append((field_name.name, label))

        return field_choices
