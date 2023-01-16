from api.v1.views.page_views import PageViewSet, UserPageViewSet
from api.v1.views.post_views import PostViewSet
from api.v1.views.user_views import (
    JSONWebTokenAuthViewSet,
    UserRegisterViewSet,
    UserViewSet,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("user", UserViewSet, basename="user")
router.register("post", PostViewSet, basename="post")
router.register("page", PageViewSet, basename="page")
router.register("user_page", UserPageViewSet, basename="user_page")
router.register("register", UserRegisterViewSet, basename="user_register")
router.register("login", JSONWebTokenAuthViewSet, basename="login")

urlpatterns = router.urls
