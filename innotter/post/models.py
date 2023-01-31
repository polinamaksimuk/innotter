from api.v1.services.managers import PostManager
from django.db import models
from page.models import Page


class Post(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="posts")
    content = models.CharField(max_length=180)

    reply_to = models.ForeignKey("post.Post", on_delete=models.SET_NULL, null=True, blank=True, related_name="replies")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    users_liked = models.ManyToManyField(
        "person.User",
        blank=True,
        null=True,
        related_name="liked_posts",
    )

    objects = PostManager()

    def __str__(self):
        return f"id: {self.pk}, page: {self.page.name}"

    def get_absolute_url(self):
        return f"/posts/{self.pk}/"

    @property
    def total_likes(self):
        return self.users_liked.count()
