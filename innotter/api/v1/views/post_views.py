from api.v1.serializers.post_serializers import (
    CreatePostSerializer,
    LikesSerializer,
    ListPostSerializer,
    PostSerializer,
    RetrievePostSerializer,
    UpdatePostSerializer,
)
from api.v1.services.post_services import PostServices
from django.shortcuts import get_object_or_404
from page.models import Page
from page.permissions import *
from post.models import Post
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class PostViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = []
    permissions_dict = {
        "create": (
            permissions.IsAuthenticated,
            IsPageOwner,
        ),
        "list": (
            permissions.IsAuthenticated,
            PageIsntBlocked,
        ),
        "retrieve": (
            permissions.IsAuthenticated,
            PageIsntBlocked,
        ),
        "update": (
            permissions.IsAuthenticated,
            IsPageOwner,
            PageIsntBlocked,
        ),
        "partial_update": (
            permissions.IsAuthenticated,
            IsPageOwner,
            PageIsntBlocked,
        ),
        "destroy": (
            permissions.IsAuthenticated,
            IsPageOwnerOrModeratorOrAdmin,
            PageIsntBlocked,
        ),
        "like": (
            permissions.IsAuthenticated,
            PageIsPublic,
            PageIsntBlocked,
        ),
        "total_likes": (
            permissions.IsAuthenticated,
            PageIsPublic,
            PageIsntBlocked,
        ),
    }

    serializer_classes = {
        "create": CreatePostSerializer,
        "update": UpdatePostSerializer,
        "partial_update": UpdatePostSerializer,
        "retrieve": RetrievePostSerializer,
        "list": ListPostSerializer,
        "total_likes": LikesSerializer,
    }

    def get_queryset(self):
        parent_page_id = self.kwargs.get("parent_lookup_page_id")
        return Post.objects.get_posts_of_page(parent_page_id)

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action)

    def get_permissions(self):
        permissions_classes = self.permissions_dict.get(self.action)
        return [permission() for permission in permissions_classes]

    def list(self, request, *args, **kwargs):
        parent_page_id = self.kwargs.get("parent_lookup_page_id")
        page = get_object_or_404(Page, pk=parent_page_id)
        self.check_object_permissions(request, page)
        return super().list(request, args, kwargs)

    @action(detail=True, methods=["patch"])
    def like(self, request, parent_lookup_page_id=None, pk=None):
        page = get_object_or_404(Page, pk=parent_lookup_page_id)
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, page)
        PostServices.like_or_unlike_post(post, request.user)
        return Response("Success", status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def total_likes(self, request, parent_lookup_page_id=None, pk=None):
        page = get_object_or_404(Page, pk=parent_lookup_page_id)
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, page)
        serializer_classes = self.get_serializer_class()
        serializer = serializer_classes(post)
        return Response(serializer.data, status=status.HTTP_200_OK)
