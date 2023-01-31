from api.v1.serializers.post_serializers import PostSerializer
from api.v1.services.post_services import PostServices
from django.shortcuts import get_object_or_404
from page.models import Page
from page.permissions import *
from post.models import Post
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class PostViewSet(viewsets.ModelViewSet):
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
    }

    def get_queryset(self):
        parent_page_id = self.kwargs.get("parent_lookup_page_id")
        return Post.objects.get_posts_of_page(parent_page_id)

    def get_permissions(self):
        if self.action in self.permissions_dict:
            perms = self.permissions_dict[self.action]
        else:
            perms = []
        return [permission() for permission in perms]

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
        total_likes = post.total_likes
        return Response({"total_likes": total_likes}, status=status.HTTP_200_OK)
