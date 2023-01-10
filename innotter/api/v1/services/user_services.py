import datetime

import jwt
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist


def generate_access_token(user):
    token = jwt.encode(
        {
            "username": user.username,
            "iat": datetime.datetime.utcnow(),
            "nbf": datetime.datetime.utcnow() + datetime.timedelta(minutes=-5),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
        },
        settings.SECRET_KEY,
    )
    return token


def generate_refresh_token(user):
    refresh_token = jwt.encode(
        {
            "username": user.username,
            "iat": datetime.datetime.utcnow(),
            "nbf": datetime.datetime.utcnow() + datetime.timedelta(minutes=-5),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
        },
        settings.SECRET_KEY,
    )

    return refresh_token


def get_refresh_token_obj(refresh_token):
    try:
        old_token = cache.get(refresh_token)
    except ObjectDoesNotExist:
        return None
    return old_token


def set_refresh_token(refresh_token):
    cache.set(refresh_token, refresh_token)


def check_and_update_refresh_token(refresh_token, user):
    old_token = get_refresh_token_obj(refresh_token)
    if old_token:
        new_access_token = generate_access_token(user)
        new_refresh_token = generate_refresh_token(user)
        set_refresh_token(new_refresh_token)
        cache.delete(old_token)
        return {
            settings.CUSTOM_JWT["AUTH_COOKIE"]: new_access_token,
            settings.CUSTOM_JWT["AUTH_COOKIE_REFRESH"]: new_refresh_token,
        }
