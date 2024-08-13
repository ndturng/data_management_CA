# Generated by Django 5.1 on 2024-08-12 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Person",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("date_of_birth", models.DateField()),
                ("address", models.TextField()),
                ("id_ca", models.CharField(max_length=255)),
            ],
        ),
    ]
