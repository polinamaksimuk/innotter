from api.v1.serializers.page_serializers import PageUserSerializer, TagSerializer
from page.models import Page, Tag
from page.permissions import *
from rest_framework import status, viewsets
from rest_framework.response import Response


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageUserSerializer
    permission_classes = []
    permissions_dict = {
        "partial_update": IsPageOwnerOrModeratorOrAdmin,
        "update": IsPageOwnerOrModeratorOrAdmin,
        "destroy": IsPageOwner,
        "create": (permissions.IsAuthenticated,),
        "list": (permissions.IsAuthenticated,),
    }

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


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
