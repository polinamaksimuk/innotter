from api.v1.serializers.user_serializers import UserSerializer
from page.models import Page, Tag
from rest_framework import serializers


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["name"]


class PageSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    followers = UserSerializer(many=True)
    owner = UserSerializer()
    follow_requests = UserSerializer(many=True)

    class Meta:
        model = Page
        depth = 1
        fields = ["name", "uuid", "description", "image", "owner", "followers", "follow_requests", "tags"]
