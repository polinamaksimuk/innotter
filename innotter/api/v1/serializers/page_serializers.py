from api.v1.serializers.user_serializers import UserSerializer
from page.models import Page, Tag
from person.models import User
from rest_framework import serializers


class PageListSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Page
        fields = (
            "id",
            "name",
            "uuid",
            "owner",
            "is_private",
            "is_blocked",
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["name"]


class PageUserSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    followers = UserSerializer(many=True)
    owner = UserSerializer()
    follow_requests = UserSerializer(many=True)
    tags = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Tag.objects.all())
    is_private = serializers.BooleanField(required=True)

    class Meta:
        model = Page
        depth = 1
        fields = ["name", "uuid", "description", "image", "owner", "followers", "follow_requests", "tags", "is_private"]
        read_only_fields = ("unblock_date", "owner")


class AdminPageDetailSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name", allow_null=True)
    followers = serializers.SlugRelatedField(many=True, read_only=True, slug_field="username", allow_null=True)
    is_blocked = serializers.BooleanField()

    class Meta:
        model = Page
        fields = (
            "id",
            "name",
            "uuid",
            "description",
            "tags",
            "owner",
            "followers",
            "is_private",
            "unblock_date",
            "is_blocked",
        )
        read_only_fields = (
            "id",
            "name",
            "uuid",
            "description",
            "tags",
            "owner",
            "image_s3_path",
            "followers",
            "is_private",
        )


class ModerPageDetailSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name", allow_null=True)
    followers = serializers.SlugRelatedField(many=True, read_only=True, slug_field="username", allow_null=True)
    unblock_date = serializers.DateTimeField(required=True)

    class Meta:
        model = Page
        fields = (
            "id",
            "name",
            "uuid",
            "description",
            "tags",
            "owner",
            "followers",
            "is_private",
            "unblock_date",
            "is_blocked",
        )
        read_only_fields = (
            "id",
            "name",
            "uuid",
            "description",
            "tags",
            "owner",
            "image_s3_path",
            "followers",
            "is_private",
            "is_blocked",
        )


class FollowersListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "title",
            "email",
        )


class FollowerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ("email",)
