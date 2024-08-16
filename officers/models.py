from django.db import models


class Officer(models.Model):
    id_ca = models.CharField(max_length=255, default="unknown")
    id_citizen = models.CharField(max_length=255, default="unknown")
    name = models.CharField(max_length=255, default="unknown")
    gender = models.CharField(max_length=255, default="unknown")
    date_of_birth = models.DateField(
        null=True
    )  # handle the case just the month and year
    date_of_enlistment = models.DateField(null=True)
    date_join_party = models.DateField(null=True)
    home_town = models.CharField(max_length=255, default="unknown")
    current_residence = models.CharField(
        max_length=255, default="unknown"
    )  # address
    blood_type = models.CharField(max_length=255, default="unknown")
    education = models.CharField(max_length=255, default="unknown")
    certi_of_IT = models.CharField(max_length=255, default="unknown")
    certi_of_foreign_language = models.CharField(
        max_length=255, default="unknown"
    )
    political_theory = models.CharField(max_length=255, default="unknown")
    military_rank = models.CharField(max_length=255, default="unknown")
    rank_type = models.CharField(max_length=255, default="unknown")
    position = models.CharField(max_length=255, default="unknown")
    work_unit = models.CharField(max_length=255, default="unknown")
    military_type = models.CharField(max_length=255, default="unknown")
    equipment_type = models.CharField(max_length=255, default="unknown")
    size_of_shoes = models.CharField(max_length=255, default="unknown")
    size_of_hat = models.CharField(max_length=255, default="unknown")
    size_of_clothes = models.CharField(max_length=255, default="unknown")
    bank_account_BIDV = models.CharField(max_length=255, default="unknown")
    phone_number = models.CharField(max_length=255, default="unknown")
    laudatory = models.CharField(max_length=255, default="unknown")
    punishment = models.CharField(max_length=255, default="unknown")

    def __str__(self):
        return self.name
