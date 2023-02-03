from django.db import models
from django.db.models.query import QuerySet


class PostManager(models.Manager):
    def get_posts_of_page(self, page_id: int) -> QuerySet:
        return self.filter(page=page_id)
