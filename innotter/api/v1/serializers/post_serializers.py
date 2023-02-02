from api.v1.serializers.page_serializers import PageUserSerializer
from post.models import Post
from rest_framework import serializers


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "page",
            "content",
            "reply_to",
            "created_at",
            "updated_at",
            "users_liked",
        )


class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "page",
            "content",
            "reply_to",
        )


class UpdatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "content",
        )


class RetrievePostSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(slug_field="email", read_only=True)
    page = serializers.SlugRelatedField(slug_field="name", read_only=True)
    reply_to = serializers.SlugRelatedField(slug_field="content", read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "owner",
            "page",
            "content",
            "reply_to",
            "created",
            "updated",
        )


class ListPostSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(slug_field="email", read_only=True)
    page = serializers.SlugRelatedField(slug_field="name", read_only=True)
    reply_to = serializers.SlugRelatedField(slug_field="content", read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "owner",
            "page",
            "content",
            "reply_to",
        )


class LikesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("total_likes",)
