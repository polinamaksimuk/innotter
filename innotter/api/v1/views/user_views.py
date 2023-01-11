import traceback

import jwt
from api.v1.serializers.user_serializers import UserRegisterSerializer, UserSerializer
from api.v1.services.user_services import (
    check_and_update_refresh_token,
    generate_access_token,
    generate_refresh_token,
    set_refresh_token,
)
from django.core.exceptions import ObjectDoesNotExist
from person.models import User
from person.permissions import *
from rest_framework import parsers, renderers, status, viewsets
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response

from innotter import settings


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []
    permissions_dict = {
        "partial_update": (permissions.IsAuthenticated, IsUserOwnerOrAdmin),
        "update": (permissions.IsAuthenticated, IsUserOwnerOrAdmin),
        "destroy": (permissions.IsAuthenticated, IsUserOwnerOrAdmin),
        "create": (permissions.AllowAny,),
        "list": (
            permissions.IsAuthenticated,
            IsAdmin,
        ),
        "retrieve": (permissions.IsAuthenticated,),
        "image": (
            permissions.IsAuthenticated,
            IsUserOwnerOrAdmin,
        ),
    }

    def get_permissions(self):
        if self.action in self.permissions_dict:
            perms = self.permissions_dict[self.action]
        else:
            perms = []
        return [permission() for permission in perms]


class UserRegisterViewSet(CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={"message": "Registration completed successfully. Now login!"}, status=status.HTTP_200_OK
            )
        return Response(data={"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class JSONWebTokenAuthViewSet(viewsets.ViewSet):
    throttle_classes = ()
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token = generate_access_token(user)
            refresh_token = generate_refresh_token(user)
            set_refresh_token(refresh_token)
            response = Response({"token": token, "refresh_token": refresh_token})
            response.set_cookie(
                key=settings.CUSTOM_JWT["AUTH_COOKIE"],
                value=token,
                expires=settings.CUSTOM_JWT["ACCESS_TOKEN_LIFETIME"],
                secure=settings.CUSTOM_JWT["AUTH_COOKIE_SECURE"],
                httponly=settings.CUSTOM_JWT["AUTH_COOKIE_HTTP_ONLY"],
                samesite=settings.CUSTOM_JWT["AUTH_COOKIE_SAMESITE"],
            )
            response.set_cookie(
                key=settings.CUSTOM_JWT["AUTH_COOKIE_REFRESH"],
                value=refresh_token,
                expires=settings.CUSTOM_JWT["REFRESH_TOKEN_LIFETIME"],
                secure=settings.CUSTOM_JWT["AUTH_COOKIE_SECURE"],
                httponly=settings.CUSTOM_JWT["AUTH_COOKIE_HTTP_ONLY"],
                samesite=settings.CUSTOM_JWT["AUTH_COOKIE_SAMESITE"],
            )

            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=("post",), detail=False, url_path="refresh", url_name="refresh")
    def refresh(self, request):
        refresh_token = request.COOKIES.get(settings.CUSTOM_JWT["AUTH_COOKIE_REFRESH"])
        if refresh_token:
            try:
                user_jwt = jwt.decode(
                    refresh_token,
                    settings.SECRET_KEY,
                    algorithms=["HS256"],
                )
                user_jwt = User.objects.get(username=user_jwt["username"])
                new_tokens = check_and_update_refresh_token(refresh_token, user_jwt)

                if new_tokens:
                    response = Response(new_tokens)
                    response.set_cookie(
                        key=settings.CUSTOM_JWT["AUTH_COOKIE"],
                        value=new_tokens[settings.CUSTOM_JWT["AUTH_COOKIE"]],
                        expires=settings.CUSTOM_JWT["ACCESS_TOKEN_LIFETIME"],
                        secure=settings.CUSTOM_JWT["AUTH_COOKIE_SECURE"],
                        httponly=settings.CUSTOM_JWT["AUTH_COOKIE_HTTP_ONLY"],
                        samesite=settings.CUSTOM_JWT["AUTH_COOKIE_SAMESITE"],
                    )
                    response.set_cookie(
                        key=settings.CUSTOM_JWT["AUTH_COOKIE_REFRESH"],
                        value=new_tokens[settings.CUSTOM_JWT["AUTH_COOKIE_REFRESH"]],
                        expires=settings.CUSTOM_JWT["REFRESH_TOKEN_LIFETIME"],
                        secure=settings.CUSTOM_JWT["AUTH_COOKIE_SECURE"],
                        httponly=settings.CUSTOM_JWT["AUTH_COOKIE_HTTP_ONLY"],
                        samesite=settings.CUSTOM_JWT["AUTH_COOKIE_SAMESITE"],
                    )

                    return response

            except (ObjectDoesNotExist, jwt.exceptions.ExpiredSignatureError):
                traceback.print_exc()

        return Response({"message": "Your token isn't valid"})
