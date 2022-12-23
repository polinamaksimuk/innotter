from api.v1.serializers.page_serializers import PageSerializer
from post.models import Post
from rest_framework import serializers


class PostSerializer(serializers.ModelSerializer):
    page = PageSerializer()

    class Meta:
        model = Post
        depth = 1
        fields = ["page", "content", "reply_to"]
