from django.db import models

# Create your models here.
class Person(models.Model):
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    address = models.TextField()
    id_ca = models.CharField(max_length=255)

    def __str__(self):
        return self.name


