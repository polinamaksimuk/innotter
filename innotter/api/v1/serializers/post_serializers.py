from api.v1.serializers.page_serializers import PageUserSerializer
from post.models import Post
from rest_framework import serializers


class PostSerializer(serializers.ModelSerializer):
    page = PageUserSerializer()

    class Meta:
        model = Post
        depth = 1
        fields = ["page", "content", "reply_to"]
