from api.v1.views.page_views import PageViewSet
from api.v1.views.post_views import PostViewSet
from api.v1.views.user_views import UserRegisterViewSet, UserViewSet
from django.urls import path
from rest_framework import routers
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("user", UserViewSet, basename="user")
router.register("post", PostViewSet, basename="post")
router.register("page", PageViewSet, basename="page")
router.register("register", UserRegisterViewSet, basename="user_register")


urlpatterns = router.urls
