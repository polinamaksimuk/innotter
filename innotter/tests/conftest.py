import pytest
from django.contrib.auth.models import AnonymousUser
from faker import Faker
from model_bakery import baker
from person.models import User
from rest_framework.test import APIClient


@pytest.fixture
def user_password() -> str:
    return "password"


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user_for_serializer():
    faker = Faker()
    return {
        "username": faker.first_name(),
        "email": faker.email(),
        "role": "user",
        "title": faker.name(),
        "password": faker.password(),
    }


@pytest.fixture()
def _request(mocker):
    return mocker.MagicMock()


@pytest.fixture()
def anon():
    return AnonymousUser()


@pytest.fixture()
def user():
    return baker.make(User, role="user")


@pytest.fixture()
def moder():
    return baker.make(User, role="moderator")


@pytest.fixture()
def admin():
    return baker.make(User, role="admin")
