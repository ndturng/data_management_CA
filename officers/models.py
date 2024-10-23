import os
import unicodedata

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from officers.utils import cal_next_rank


# flake8: noqa
class Officer(models.Model):
    # Số hiệu - Số hồ sơ
    id_ca = models.CharField(
        max_length=255, null=True, blank=True, unique=True,
    )
    # Họ và tên khai sinh
    birth_name = models.CharField(max_length=255, null=True, blank=False)
    # Tên đang dùng
    current_name = models.CharField(max_length=255, null=True, blank=False)
    # Giới tính
    gender = models.CharField(max_length=255, null=True, blank=False)
    # Nơi sinh
    birth_place = models.CharField(
        max_length=255, null=True, blank=True, 
    )
    # Chỗ ở hiện nay
    current_residence = models.CharField(max_length=255, null=True, blank=False)
    # Dân tộc
    folk = models.CharField(
        max_length=255, null=True, blank=True, default="Kinh"
    )
    # Tôn giáo
    religion = models.CharField(
        max_length=255, null=True, blank=True, default="Không"
    )
    # Ngày sinh
    date_of_birth = models.DateField(
        null=True, blank=True,
    )  # handle the case just the month and year
    # Năm sinh # added field
    birth_year = models.IntegerField(null=True, blank=True, default=1800)
    # Tháng năm vào Đoàn
    month_join_group = models.CharField(max_length=7, null=True, blank=True)
    # Đoàn thể
    group = models.CharField(
        max_length=255, null=True, blank=True,
    )

    # Tháng năm vào Đảng
    month_join_party = models.CharField(max_length=7, null=True, blank=True)
    # Năm vào Đảng # added field
    year_join_party = models.IntegerField(null=True, blank=True)
    # Tháng năm chính thức
    month_join_party_official = models.CharField(
        max_length=7, null=True, blank=True
    )
    # Năm chính thức # added field
    year_join_party_official = models.IntegerField(null=True, blank=True)
    # Số thẻ Đảng
    party_card_number = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Chức vụ Đảng
    party_position = models.CharField(
        max_length=255, null=True, blank=True, default="Đảng viên"
    )
    
    # Tháng năm tuyển dụng
    month_recruit = models.CharField(max_length=7, null=True, blank=True)
    # Tháng năm vào CA
    month_join_CA = models.CharField(max_length=7, null=True, blank=True)
    # Năm vào CA # added field
    year_join_CA = models.IntegerField(null=True, blank=True)
    # Đơn vị tuyển
    recruit_unit = models.CharField(
        max_length=255, null=True, blank=True, default="Công an tỉnh Phú Yên"
    )
    # Nguồn tuyển
    recruit_source = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Ký hiệu đơn vị
    unit_notation = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Chức vụ
    position = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Cấp bậc
    military_rank = models.CharField(
        max_length=255, null=True, blank=True, 
    )
    # Hệ số lương
    salary_coefficient = models.FloatField(null=True, blank=True, default=4.2)
    # Quyết định lương
    salary_decision = models.CharField(
        max_length=255, null=True, blank=True, 
    )
    # Năm quyết định lương
    salary_decision_year = models.IntegerField(
        null=True, blank=True,
    )
    # Hệ số lương tiếp theo
    next_salary_coefficient = models.FloatField(
        null=True, blank=True, default=4.6
    )
    # Năm quyết định lương tiếp theo
    next_salary_decision_year = models.IntegerField(
        null=True, blank=True,
    )
    # Đơn vị công tác
    work_unit = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Lực lượng
    military_type = models.CharField(
        max_length=255, null=True, blank=True, 
    )
    # Loại hàm
    rank_type = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Quân trang
    equipment_type = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Giày
    size_of_shoes = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Mũ
    size_of_hat = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Quần áo
    size_of_clothes = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Công tác chuyên trách
    specialized_work = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Quyết định điều động
    maneuver_decision = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Công tác khác
    other_work = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Công tác làm nhiều nhất
    most_work = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Trình độ học vấn
    education = models.CharField(
        max_length=255, null=True, blank=True, default="12/12"
    )
    # Tin học
    certi_of_IT = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Ngoại ngữ
    certi_of_foreign_language = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Trình độ chính trị
    political_theory = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Năng lực sở trường
    strength = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Nhóm máu
    blood_type = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Danh hiệu
    compete_title = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Gia đình chính sách
    policy_family = models.CharField(
        max_length=255, null=True, blank=True, default="Không"
    )
    # Địa chỉ hồ sơ
    profile_address = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Số điện thoại
    phone_number = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Số TK BIDV
    bank_account_BIDV = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Số sổ bảo hiểm
    insurance_number = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Số CCCD
    id_citizen = models.CharField(
        max_length=255, null=True, blank=True,
    )
    # Ngày cập nhật
    date_update = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Override the save method to normalize and calculate the additional fields before saving the object
        """
        # Extract birth year from date of birth
        if self.date_of_birth:
            self.birth_year = self.date_of_birth.year
        
        # Extract year
        if self.month_join_party:
            self.year_join_party = int(self.month_join_party.split("/")[1])
        if self.month_join_party_official:
            self.year_join_party_official = int(self.month_join_party_official.split("/")[1])
        if self.month_join_CA:
            self.year_join_CA = int(self.month_join_CA.split("/")[1])

        # Normalize name fields to NFC # normalize all the fields to NFC # other models
        if self.birth_name:
            self.birth_name = unicodedata.normalize("NFC", self.birth_name)
        if self.current_name:
            self.current_name = unicodedata.normalize("NFC", self.current_name)

        # Calculate next salary coefficient and decision year
        if self.salary_coefficient and self.salary_decision_year:
            self.next_salary_coefficient, self.next_salary_decision_year = (
                cal_next_rank(
                    self.salary_coefficient, self.salary_decision_year
                )
            )

        if self.phone_number:
            self.phone_number = str(self.phone_number).split(".")[0]
        if self.id_citizen:
            self.id_citizen = str(self.id_citizen).split(".")[0]
        if self.size_of_clothes:
            self.size_of_clothes = str(self.size_of_clothes).split(".")[0]

        super(Officer, self).save(*args, **kwargs)

    def __str__(self):
        return self.birth_name


class Title(models.Model):  # Chức danh
    officer = models.ForeignKey(
        Officer, on_delete=models.CASCADE, related_name="titles"
    )
    appointed_date = models.DateField(null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title


class PositionPlan(models.Model):  # Quy hoạch
    officer = models.ForeignKey(
        Officer, on_delete=models.CASCADE, related_name="position_plans"
    )
    period = models.CharField(max_length=11, null=True, blank=True)
    position = models.CharField(max_length=255, null=True, blank=True)


class LearningPath(models.Model):  # Đào tạo
    officer = models.ForeignKey(
        Officer, on_delete=models.CASCADE, related_name="learning_paths"
    )
    period = models.CharField(max_length=11, null=True, blank=True)
    learning_content = models.CharField(max_length=255, null=True, blank=True)


class WorkProcess(models.Model):  # Quá trình công tác
    officer = models.ForeignKey(
        Officer, on_delete=models.CASCADE, related_name="work_processes"
    )
    period = models.CharField(max_length=11, null=True, blank=True)
    work_content = models.CharField(max_length=255, null=True, blank=True)


class SalaryProcess(models.Model):  # Quá trình lương
    officer = models.ForeignKey(
        Officer, on_delete=models.CASCADE, related_name="salary_processes"
    )
    time = models.IntegerField(null=True, blank=True)
    mil_rank = models.CharField(max_length=255, null=True, blank=True)
    salary_coefficient = models.FloatField(null=True, blank=True)


class Laudatory(models.Model):  # Khen thưởng
    officer = models.ForeignKey(
        Officer, on_delete=models.CASCADE, related_name="laudatories"
    )
    time = models.IntegerField(null=True, blank=True)
    form = models.CharField(max_length=255, null=True, blank=True)
    content = models.CharField(max_length=255, null=True, blank=True)


class Discipline(models.Model):  # Kỷ luật
    officer = models.ForeignKey(
        Officer, on_delete=models.CASCADE, related_name="disciplines"
    )
    time = models.IntegerField(null=True, blank=True)
    form = models.CharField(max_length=255, null=True, blank=True)
    content = models.CharField(max_length=255, null=True, blank=True)


class Relative(models.Model):  # Thân nhân
    officer = models.ForeignKey(
        Officer, on_delete=models.CASCADE, related_name="relatives"
    )
    relationship = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    birth_year = models.IntegerField(null=True, blank=True)
    job = models.CharField(max_length=255, null=True, blank=True)
    current_residence = models.CharField(max_length=255, null=True, blank=True)


class Abroad(models.Model):  # Ra nước ngoài
    officer = models.ForeignKey(
        Officer, on_delete=models.CASCADE, related_name="abroads"
    )
    time = models.IntegerField(null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    purpose = models.CharField(max_length=255, null=True, blank=True)


class ArmyJoinHistory(models.Model):  # Tham gia quân đội
    officer = models.ForeignKey(
        Officer, on_delete=models.CASCADE, related_name="army_join_histories"
    )
    period = models.CharField(max_length=11, null=True, blank=True)
    unit = models.CharField(max_length=255, null=True, blank=True)
    form = models.CharField(max_length=255, null=True, blank=True)


class Health(models.Model):  # Sức khoẻ
    officer = models.ForeignKey(
        Officer, on_delete=models.CASCADE, related_name="healths"
    )
    weight = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    medical_history = models.CharField(max_length=255, null=True, blank=True)
    other = models.CharField(max_length=255, null=True, blank=True)


class Image(models.Model):  # Hình ảnh
    officer = models.ForeignKey(
        Officer, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(
        upload_to="officer_images/", null=True, blank=True
    )
    description = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        # If replacing an image, delete the old file
        try:
            this = Image.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete(save=False)
        except Image.DoesNotExist:
            pass  # This is the first save, so no replacement needed
        super().save(*args, **kwargs)

    def __str__(self):
        return self.description


@receiver(post_delete, sender=Image)
def delete_image_file(sender, instance, **kwargs):
    # Check if the image file exists and delete it
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
