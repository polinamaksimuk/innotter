from api.v1.serializers.page_serializers import PageSerializer, TagSerializer
from page.models import Page, Tag
from rest_framework import viewsets


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
