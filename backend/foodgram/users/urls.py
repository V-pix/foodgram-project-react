from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import (
    AuthTokenView,
    CustomUserViewSet,
    SubscribtionViewSet,
    UserRegistrationView,
)

app_name = 'users'

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(
    r'users/(?P<author_id>\d+)/subscribe', SubscribtionViewSet, basename='subscribe'
)

urlpatterns = [
    # path('auth/signup/', UserRegistrationView.as_view(), name='signup'),
    # path('auth/token/login/', AuthTokenView.as_view(), name='auth'),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    # path('users/subscriptions/'),
    # path('users/<int:post_id>/subscribe/'),
]
