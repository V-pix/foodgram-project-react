from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet

app_name = "users"

router = DefaultRouter()
router.register(r"users", CustomUserViewSet, basename="users")


urlpatterns = [
    path(
        "users/subscriptions/",
        CustomUserViewSet.as_view(
            {
                "get": "subscriptions",
            }
        ),
        name="subscriptions",
    ),
    path("auth/", include("djoser.urls.authtoken")),
    path("", include("djoser.urls")),
    path("", include(router.urls)),
]
