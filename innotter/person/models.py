from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        USER = "user"
        MODERATOR = "moderator"
        ADMIN = "admin"

    email = models.EmailField(unique=True)
    image_s3_path = models.ImageField(
        upload_to="innotter/media", null=True, height_field=None, width_field=None, max_length=100
    )
    role = models.CharField(max_length=9, choices=Roles.choices)

    title = models.CharField(max_length=80)
    is_blocked = models.BooleanField(default=False)
