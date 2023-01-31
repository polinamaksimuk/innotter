from api.v1.serializers.page_serializers import PageUserSerializer
from post.models import Post
from rest_framework import serializers


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            "page",
            "content",
            "reply_to",
            "created_at",
            "updated_at",
            "users_liked",
        ]
