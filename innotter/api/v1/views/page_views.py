from api.v1.serializers.page_serializers import PageUserSerializer, TagSerializer
from page.models import Page, Tag
from page.permissions import *
from rest_framework import viewsets


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageUserSerializer
    permission_classes = []
    permissions_dict = {
        "partial_update": (permissions.IsAuthenticated, IsPageOwnerOrModeratorOrAdmin),
        "update": (permissions.IsAuthenticated, IsPageOwnerOrModeratorOrAdmin),
        "destroy": (permissions.IsAuthenticated, IsPageOwner),
        "create": (permissions.IsAuthenticated,),
        "list": (permissions.IsAuthenticated,),
        "retrieve": (permissions.IsAuthenticated),
        "follow_requests": (permissions.IsAuthenticated, IsPageOwnerOrModeratorOrAdmin),
        "followers": (permissions.IsAuthenticated, IsPageOwnerOrModeratorOrAdmin),
        "follow": (permissions.IsAuthenticated),
        "posts": (permissions.IsAuthenticated),
        "image": (
            permissions.IsAuthenticated,
            IsPageOwnerOrModeratorOrAdmin,
        ),
    }

    def get_permissions(self):
        if self.action in self.permissions_dict:
            perms = self.permissions_dict[self.action]
        else:
            perms = []
        return [permission() for permission in perms]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
