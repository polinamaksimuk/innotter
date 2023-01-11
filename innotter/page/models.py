from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Page(models.Model):
    name = models.CharField(max_length=80)
    uuid = models.CharField(max_length=30, unique=True)
    description = models.TextField()
    tags = models.ManyToManyField("page.Tag", related_name="pages")

    owner = models.ForeignKey("person.User", on_delete=models.CASCADE, related_name="pages")
    followers = models.ManyToManyField("person.User", related_name="follows")

    image = models.ImageField(
        upload_to="innotter/media", null=True, height_field=None, width_field=None, max_length=100
    )

    is_private = models.BooleanField(default=False)
    follow_requests = models.ManyToManyField("person.User", related_name="requests")
    unblock_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
