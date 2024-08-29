from django.db import models

# flake8: noqa
class Officer(models.Model):  
    name = models.CharField(max_length=255, null=True, blank=False)
    id_ca = models.CharField(max_length=255, null=True, blank=True, unique=True, default="nan") 
    id_citizen = models.CharField(max_length=255, null=True, blank=True, default="nan")
    gender = models.CharField(max_length=255, null=True, blank=False)

    date_of_birth = models.DateField(null=True, blank=True, default="nan")  # handle the case just the month and year 
    birth_year = models.IntegerField(null=True, blank=True, default="nan")

    date_of_enlistment = models.DateField(null=True, blank=True, default="nan")
    enlistment_year = models.IntegerField(null=True, blank=True, default="nan")

    date_join_party = models.DateField(null=True, blank=True, default="nan")
    join_party_year = models.IntegerField(null=True, blank=True, default="nan")

    home_town = models.CharField(max_length=255, null=True, blank=False)
    current_residence = models.CharField(
        max_length=255, null=True, blank=False
    )  # address
    blood_type = models.CharField(max_length=255, null=True, blank=True, default="nan")
    education = models.CharField(max_length=255, null=True, blank=True, default="nan")
    certi_of_IT = models.CharField(max_length=255, null=True, blank=True, default="nan")
    certi_of_foreign_language = models.CharField(
        max_length=255, null=True, blank=True, default="nan"
    )
    political_theory = models.CharField(max_length=255, null=True, blank=True, default="nan")
    military_rank = models.CharField(max_length=255, null=True, blank=True, default="nan") 
    rank_type = models.CharField(max_length=255, null=True, blank=True, default="nan")
    position = models.CharField(max_length=255, null=True, blank=True, default="nan")
    work_unit = models.CharField(max_length=255, null=True, blank=True, default="nan")
    military_type = models.CharField(max_length=255, null=True, blank=True, default="nan")
    equipment_type = models.CharField(max_length=255, null=True, blank=True, default="nan")
    size_of_shoes = models.CharField(max_length=255, null=True, blank=True, default="nan")
    size_of_hat = models.CharField(max_length=255, null=True, blank=True, default="nan")
    size_of_clothes = models.CharField(max_length=255, null=True, blank=True, default="nan")
    bank_account_BIDV = models.CharField(max_length=255, null=True, blank=True, default="nan")
    phone_number = models.CharField(max_length=255, null=True, blank=True, default="nan")
    laudatory = models.CharField(max_length=255, null=True, blank=True, default="nan")
    punishment = models.CharField(max_length=255, null=True, blank=True, default="nan")

    def __str__(self):
        return self.name
