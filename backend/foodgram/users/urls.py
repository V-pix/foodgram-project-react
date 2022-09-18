from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import AuthTokenView, CustomUserViewSet, UserRegistrationView

app_name = 'users'

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    # path('auth/signup/', UserRegistrationView.as_view(), name='signup'),
    # path('auth/token/login/', AuthTokenView.as_view(), name='auth'),
    path('', include('djoser.urls')),
    # url(r'^auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    # path('auth/', include('djoser.urls.jwt')),
    # path('users/subscriptions/'),
    # path('users/set_password/'),
]
