from api.v1.serializers.page_serializers import (
    AdminPageDetailSerializer,
    FollowersListSerializer,
    FollowersSerializer,
    FollowRequestsSerializer,
    ModerPageDetailSerializer,
    PageListSerializer,
    PageUserSerializer,
    TagSerializer,
)
from django.shortcuts import get_object_or_404
from page.models import Page, Tag
from page.permissions import *
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    permission_classes = []
    permissions_dict = {
        "partial_update": (IsPageOwnerOrModeratorOrAdmin,),
        "update": (IsPageOwnerOrModeratorOrAdmin,),
        "destroy": (IsPageOwner,),
        "create": (permissions.IsAuthenticated,),
        "list": (permissions.IsAuthenticated,),
        "retrieve": (
            IsAdminOrModerator,
            PageIsPublicOrOwner,
            PageIsntBlocked,
        ),
        "blocked": (
            permissions.IsAuthenticated,
            IsAdminOrModerator,
        ),
        "follow-requests": (
            IsPageOwnerOrModeratorOrAdmin,
            PageIsntBlocked,
        ),
        "followers": (permissions.IsAuthenticated, IsPageOwnerOrModeratorOrAdmin, PageIsntBlocked),
        "follow": (
            permissions.IsAuthenticated,
            PageIsntBlocked,
        ),
        "posts": (
            permissions.IsAuthenticated,
            PageIsntBlocked,
            PageIsPublicOrFollowerOrOwnerOrModeratorOrAdmin,
        ),
    }

    role_serializer_classes = {
        "admin": AdminPageDetailSerializer,
        "moderator": ModerPageDetailSerializer,
        "user": PageUserSerializer,
    }

    list_serializer_classes = {
        "list": PageListSerializer,
        "blocked": PageListSerializer,
        "followers": FollowersListSerializer,
    }

    filter_backends = (SearchFilter,)
    search_fields = (
        "name",
        "uuid",
        "tags__name",
    )

    def get_permissions(self):
        if self.action in self.permissions_dict:
            perms = self.permissions_dict[self.action]
        else:
            perms = []
        return [permission() for permission in perms]

    def check_permissions(self, request):
        try:
            obj = Page.objects.get(id=self.kwargs.get("pk"))
        except Page.DoesNotExist:
            return Response({"message": "Not found"}, status.HTTP_404_NOT_FOUND)
        else:
            self.check_object_permissions(request, obj)
        finally:
            return super().check_permissions(request)

    def get_queryset(self):
        if self.request.user.role in ("admin", "moderator"):
            return Page.objects.all().order_by("id")
        return PageServices.get_unblocked_pages(is_owner_page=False)

    def get_serializer_class(self):
        if self.action in ("retrieve", "update", "partial_update", "follow", "unfollow"):
            return self.role_serializer_classes.get(self.request.user.role)
        return self.list_serializer_classes.get(self.action)

    @action(detail=False, methods=("get",))
    def blocked(self, request):
        all_blocked_pages = PageServices.get_blocked_pages()
        serializer = self.get_serializer(all_blocked_pages, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=("get",), url_path="follow_requests")
    def follow_requests(self, request, pk=None):
        page = self.get_object()
        self.check_permissions(request)
        self.check_object_permissions(request, page)
        if page.is_private:
            serializer = FollowRequestsSerializer(page)
            return Response(serializer.data, status.HTTP_200_OK)
        return Response({"message": "Your page isn't private"}, status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=("get",))
    def followers(self, request, pk=None):
        page = self.get_object()
        self.check_permissions(request)
        self.check_object_permissions(request, page)
        serializer = FollowersSerializer(page)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(detail=True, methods=("post",), url_path="follow")
    def follow(self, request, pk=None):
        page = self.get_object()
        self.check_permissions(request)
        self.check_object_permissions(request, self.get_object())
        if PageServices.is_user_in_page_follow_requests(request.user, page) or PageServices.is_user_in_page_followers(
            request.user, page
        ):
            return Response({"message": "You are already sent follow request"}, status.HTTP_400_BAD_REQUEST)
        if page.is_private:
            PageServices.add_user_to_page_follow_requests(request.user, page)
        else:
            PageServices.add_user_to_page_followers(request.user, page)
        return Response({"message": "Ok"}, status.HTTP_200_OK)

    @action(detail=True, methods=("post",), url_path="unfollow")
    def unfollow(self, request, pk=None):
        page = get_object_or_404(Page, pk=pk)
        self.check_object_permissions(request, self.get_object())
        if PageServices.is_user_in_page_followers(request.user, page):
            PageServices.remove_user_from_followers(page, request.user)
            return Response(
                {"message": "You have successfully unsubscribed from the page"}, status.HTTP_400_BAD_REQUEST
            )
        return Response({"message": "You have not subscribed to this page"}, status.HTTP_200_OK)

    @action(detail=True, methods=["patch"])
    def accept(self, request, pk=None):
        page = get_object_or_404(Page, pk=pk)
        self.check_object_permissions(request, page)
        PageServices.add_user_to_followers(page, request.data.get("user_id", None))
        return Response("Success", status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"])
    def accept_all(self, request, pk=None):
        page = get_object_or_404(Page, pk=pk)
        self.check_object_permissions(request, page)
        PageServices.add_all_users_to_followers(page)
        return Response("Success", status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"])
    def deny(self, request, pk=None):
        page = get_object_or_404(Page, pk=pk)
        self.check_object_permissions(request, page)
        PageServices.remove_user_from_requests(page, request.data.get("user_id", None))
        return Response("Success", status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"])
    def deny_all(self, request, pk=None):
        page = get_object_or_404(Page, pk=pk)
        self.check_object_permissions(request, page)
        PageServices.remove_all_users_from_requests(page)
        return Response("Success", status=status.HTTP_200_OK)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = ()
    permissions_dict = {
        "destroy": IsAdminOrModerator,
        "create": IsAdminOrModerator,
        "list": (permissions.IsAuthenticated,),
        "retrieve": (permissions.IsAuthenticated,),
    }

    def get_permissions(self):
        if self.action in self.permissions_dict:
            perms = self.permissions_dict[self.action]
        else:
            perms = []
        return [permission() for permission in perms]
