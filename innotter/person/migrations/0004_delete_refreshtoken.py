# Generated by Django 4.1.4 on 2023-01-04 11:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("person", "0003_refreshtoken"),
    ]

    operations = [
        migrations.DeleteModel(
            name="RefreshToken",
        ),
    ]
