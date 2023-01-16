from api.v1.serializers.page_serializers import (
    AdminPageDetailSerializer,
    FollowerSerializer,
    FollowersListSerializer,
    ModerPageDetailSerializer,
    PageListSerializer,
    PageUserSerializer,
    TagSerializer,
)
from api.v1.serializers.post_serializers import PostSerializer
from api.v1.services.page_services import (
    accept_all_follow_requests,
    accept_follow_request,
    deny_follow_request,
    follow_page,
    get_blocked_pages,
    get_page_follow_requests,
    get_page_followers,
    get_unblocked_pages,
    unfollow_page,
)
from page.models import Page, Tag
from page.permissions import *
from post.models import Post
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
            PageIsPublicOrOwner,
            PageIsntBlocked,
        ),
        "blocked": (
            permissions.IsAuthenticated,
            IsAdminOrModerator,
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
        return get_unblocked_pages(is_owner_page=False)

    def get_serializer_class(self):
        if self.action in ("retrieve", "update", "partial_update", "follow", "unfollow"):
            return self.role_serializer_classes.get(self.request.user.role)
        return self.list_serializer_classes.get(self.action)

    @action(detail=False, methods=("get",))
    def blocked(self, request):
        all_blocked_pages = get_blocked_pages()
        serializer = self.get_serializer(all_blocked_pages, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=("get",))
    def followers(self, pk=None):
        all_page_followers = get_page_followers(page_pk=pk)
        serializer = self.get_serializer(all_page_followers, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=("post",))
    def follow(self, pk=None):
        is_private, page_owner_id, is_follower = follow_page(user=self.request.user, page_pk=pk)
        if not is_private:
            if not is_follower:
                data = {"method": "add", "user_id": page_owner_id, "value": "subscribers"}
                data.update()
            return Response(
                {"detail": "You have subscribed to the page or you are already a subscriber."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"detail": "You have applied for a subscription."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="unfollow")
    def unfollow(self, pk=None):
        page_owner_id, is_follower = unfollow_page(user=self.request.user, page_pk=pk)
        if is_follower:
            data = {"method": "delete", "user_id": page_owner_id, "value": "subscribers"}
            data.update()
        return Response(
            {"detail": "You have unsubscribed from the page or have already unsubscribed."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=("get",))
    def posts(self, request):
        page = self.get_object()
        self.check_permissions(request)
        self.check_object_permissions(request, page)
        query = Post.objects.filter(page=page)
        post_serializer = PostSerializer(query, many=True)
        return Response({"posts": post_serializer.data}, status.HTTP_200_OK)


class UserPageViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    serializer_classes = {
        "list": PageListSerializer,
        "create": PageListSerializer,
        "page_follow_requests": FollowersListSerializer,
        "all_follow_requests": FollowersListSerializer,
        "followers": FollowersListSerializer,
        "deny_follow_request": FollowerSerializer,
        "accept_follow_request": FollowerSerializer,
    }

    def get_queryset(self):
        return get_unblocked_pages(is_owner_page=True, owner=self.request.user)

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, PageUserSerializer)

    @action(detail=True, methods=["get"])
    def followers(self, request, pk=None):
        all_page_followers = get_page_followers(page_pk=pk)
        serializer = self.get_serializer(all_page_followers, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="follow-requests")
    def page_follow_requests(self, pk=None):
        page_follow_requests = get_page_follow_requests(page_pk=pk)
        serializer = self.get_serializer(page_follow_requests, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="accept")
    def accept_follow_request(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        is_follow_request = accept_follow_request(follower_email=email, page_pk=pk)
        if is_follow_request:
            data = {"method": "add", "user_id": self.request.user.pk, "value": "subscribers"}
            data.update()
        return Response(
            {"detail": "You have successfully accepted user to followers or user is already your follower."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="deny")
    def deny_follow_request(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        deny_follow_request(follower_email=email, page_pk=pk)
        return Response(
            {"detail": "You have successfully removed user from followers or user is already removed."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="accept-all")
    def accept_all_follow_requests(self, request, pk=None):
        follow_requests_number = accept_all_follow_requests(page_pk=pk)
        if follow_requests_number > 0:
            data = {
                "method": "add",
                "user_id": self.request.user.pk,
                "requests": follow_requests_number,
                "many": True,
                "value": "subscribers",
            }
            data.update()
        return Response({"detail": "You have successfully accepted all follow requests."}, status=status.HTTP_200_OK)


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
