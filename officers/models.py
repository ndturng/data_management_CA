from django.db import models


class Officer(models.Model):
    name = models.CharField(max_length=255, null=True, blank=False)
    id_ca = models.CharField(max_length=255, null=True, blank=True)
    id_citizen = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=False)
    date_of_birth = models.DateField(
        null=True, blank=True
    )  # handle the case just the month and year
    date_of_enlistment = models.DateField(null=True, blank=True)
    date_join_party = models.DateField(null=True, blank=True)
    home_town = models.CharField(max_length=255, null=True, blank=False)
    current_residence = models.CharField(
        max_length=255, null=True, blank=False
    )  # address
    blood_type = models.CharField(max_length=255, null=True, blank=True)
    education = models.CharField(max_length=255, null=True, blank=True)
    certi_of_IT = models.CharField(max_length=255, null=True, blank=True)
    certi_of_foreign_language = models.CharField(
        max_length=255, null=True, blank=True
    )
    political_theory = models.CharField(max_length=255, null=True, blank=True)
    military_rank = models.CharField(max_length=255, null=True, blank=True)
    rank_type = models.CharField(max_length=255, null=True, blank=True)
    position = models.CharField(max_length=255, null=True, blank=True)
    work_unit = models.CharField(max_length=255, null=True, blank=True)
    military_type = models.CharField(max_length=255, null=True, blank=True)
    equipment_type = models.CharField(max_length=255, null=True, blank=True)
    size_of_shoes = models.CharField(max_length=255, null=True, blank=True)
    size_of_hat = models.CharField(max_length=255, null=True, blank=True)
    size_of_clothes = models.CharField(max_length=255, null=True, blank=True)
    bank_account_BIDV = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    laudatory = models.CharField(max_length=255, null=True, blank=True)
    punishment = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
