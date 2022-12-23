from api.v1.serializers.post_serializers import PostSerializer
from post.models import Post
from rest_framework import viewsets


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
