from api.v1.views.page_views import PageViewSet
from api.v1.views.post_views import PostViewSet
from api.v1.views.user_views import (
    JSONWebTokenAuthViewSet,
    UserRegisterViewSet,
    UserViewSet,
)
from rest_framework_extensions.routers import ExtendedSimpleRouter

router = ExtendedSimpleRouter()
router.register("user", UserViewSet, basename="user")
router.register(r"pages", PageViewSet, basename="pages").register(
    "posts", PostViewSet, basename="pages-posts", parents_query_lookups=["page_id"]
)
router.register("register", UserRegisterViewSet, basename="user_register")
router.register("login", JSONWebTokenAuthViewSet, basename="login")

urlpatterns = router.urls
