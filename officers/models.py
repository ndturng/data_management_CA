import unicodedata

from django.db import models

from officers.utils import cal_next_rank


# flake8: noqa
class Officer(models.Model):
    # Số hiệu - Số hồ sơ
    id_ca = models.CharField(
        max_length=255, null=True, blank=True, unique=True, default="nan"
    )
    # Họ và tên khai sinh
    birth_name = models.CharField(max_length=255, null=True, blank=False)
    # Tên đang dùng
    current_name = models.CharField(max_length=255, null=True, blank=False)
    # Giới tính
    gender = models.CharField(max_length=255, null=True, blank=False)
    # Nơi sinh
    birth_place = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Chỗ ở hiện nay
    current_residence = models.CharField(max_length=255, null=True, blank=False)
    # Dân tộc
    folk = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Tôn giáo
    religion = models.CharField(
        max_length=255, null=True, blank=True, default="Không"
    )
    # Ngày sinh
    date_of_birth = models.DateField(
        null=True, blank=True, default="nan"
    )  # handle the case just the month and year
    birth_year = models.IntegerField(null=True, blank=True, default=1800)

    # Tháng năm vào Đoàn
    month_join_group = models.CharField(max_length=7, null=True, blank=True)
    # Đoàn thể
    group = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Tháng năm vào Đảng
    month_join_party = models.CharField(max_length=7, null=True, blank=True)
    # Tháng năm chính thức
    month_join_party_official = models.CharField(
        max_length=7, null=True, blank=True
    )
    # Số thẻ Đảng
    party_card_number = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Chức vụ Đảng
    party_position = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Tháng năm tuyển dụng
    month_recruit = models.CharField(max_length=7, null=True, blank=True)
    # Tháng năm vào CA
    month_join_CA = models.CharField(max_length=7, null=True, blank=True)
    # Đơn vị tuyển
    recruit_unit = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Nguồn tuyển
    recruit_source = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Ký hiệu đơn vị
    unit_notation = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Chức vụ
    position = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Cấp bậc
    military_rank = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Hệ số lương
    salary_coefficient = models.FloatField(null=True, blank=True, default=4.2)
    # Quyết định lương
    salary_decision = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Năm quyết định lương
    salary_decision_year = models.IntegerField(
        null=True, blank=True, default=1800
    )
    # Hệ số lương tiếp theo
    next_salary_coefficient = models.FloatField(
        null=True, blank=True, default=4.6
    )
    # Năm quyết định lương tiếp theo
    next_salary_decision_year = models.IntegerField(
        null=True, blank=True, default=1800
    )
    # Đơn vị công tác
    work_unit = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Lực lượng
    military_type = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Loại hàm
    rank_type = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Quân trang
    equipment_type = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Giày
    size_of_shoes = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Mũ
    size_of_hat = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Quần áo
    size_of_clothes = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Công tác chuyên trách
    specialized_work = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Quyết định điều động
    maneuver_decision = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Công tác khác
    other_work = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Công tác làm nhiều nhất
    most_work = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Trình độ học vấn
    education = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Tin học
    certi_of_IT = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Ngoại ngữ
    certi_of_foreign_language = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Trình độ chính trị
    political_theory = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Năng lực sở trường
    strength = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Nhóm máu
    blood_type = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Danh hiệu
    compete_title = models.CharField(
        max_length=255, null=True, blank=True, default="Không"
    )
    # Gia đình chính sách
    policy_family = models.CharField(
        max_length=255, null=True, blank=True, default="Không"
    )
    # Địa chỉ hồ sơ
    profile_address = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Số điện thoại
    phone_number = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Số TK BIDV
    bank_account_BIDV = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Số sổ bảo hiểm
    insurance_number = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    # Số CCCD
    id_citizen = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
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

        # Normalize name fields to NFC
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
