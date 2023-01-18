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


class PageSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name", allow_null=True)
    followers = serializers.SlugRelatedField(many=True, read_only=True, slug_field="username", allow_null=True)

    class Meta:
        model = Page
        fields = [
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
        ]
        read_only_fields = (
            "id",
            "name",
            "uuid",
            "description",
            "tags",
            "owner",
            "followers",
            "is_private",
        )


class AdminPageDetailSerializer(PageSerializer):
    is_blocked = serializers.BooleanField()

    class Meta(PageSerializer.Meta):
        fields = PageSerializer.Meta.fields
        read_only_fields = PageSerializer.Meta.read_only_fields


class ModerPageDetailSerializer(PageSerializer):
    unblock_date = serializers.DateTimeField(required=True)

    class Meta(PageSerializer.Meta):
        fields = PageSerializer.Meta.fields
        read_only_fields = PageSerializer.Meta.read_only_fields + ("is_blocked",)


class FollowRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = (
            "follow_requests",
            "followers",
        )

    def update(self, instance, validated_data):
        if validated_data["followers_accept_ids"]:
            instance.followers.add(*validated_data["followers_accept_ids"])
            if instance.follow_requests:
                instance.follow_requests.remove(*validated_data["follow_requests"])
            instance.save()
            return instance


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


class AcceptRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ("follow_requests", "followers")

    def update(self, page, validated_data):
        users = validated_data.pop("follow_requests")
        for user in users:
            page.follow_requests.remove(user)
            page.followers.add(user)
        page.save()
        return page


class DenyRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ("follow_requests",)

    def update(self, page, validated_data):
        users = validated_data.pop("follow_requests")
        for user in users:
            page.follow_requests.remove(user)
        page.save()
        return page
