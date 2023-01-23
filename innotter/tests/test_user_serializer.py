import pytest
from api.v1.serializers.user_serializers import UserSerializer
from api.v1.views.user_views import UserViewSet
from person.models import User
from rest_framework.permissions import IsAuthenticated

create_view = UserViewSet.as_view({"post": "create"})


@pytest.mark.django_db
class TestUserSerializer:
    def test_get_permissions(self):
        user_viewset = UserViewSet()
        user_viewset.action = "list"
        assert isinstance(user_viewset.get_permissions()[0], IsAuthenticated) is True

    def test_create_user(self, user_for_serializer):
        serializer = UserSerializer(data=user_for_serializer)
        if serializer.is_valid():
            serializer.save()
        assert User.objects.filter(email=user_for_serializer["email"]).first()

    def test_update_user(self, user, user_for_serializer):
        new_email = "new_email@a.com"
        user_for_serializer["email"] = new_email
        serializer = UserSerializer(instance=user, data=user_for_serializer)
        if serializer.is_valid():
            serializer.save()
        assert User.objects.filter(email=new_email).first()
