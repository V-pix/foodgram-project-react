from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import CustomUser, Subscribtion
from users.permissions import AdminPermission
from users.serializers import (
    CustomUserSerializer,
    ObtainTokenSerializer,
    RegistrationSerializer,
    SubscribtionSerializer,
)

# from users.utils import confirmation_generator


class UserRegistrationView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            username = request.data.get("username")
            # confirmation_generator(username)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthTokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ObtainTokenSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.data["username"]
            # confirmation_code = serializer.data['confirmation_code']
            user = get_object_or_404(CustomUser, username=username)
            # if confirmation_code != user.confirmation_code:
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken.for_user(user)
            return Response(
                {"token": str(token.access_token)}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    # permission_classes = (AdminPermission,)
    permission_classes = (AllowAny,)
    lookup_field = "username"

    # @action(
    # methods=['GET', 'PATCH'],
    # detail=False,
    # permission_classes=[permissions.IsAuthenticated],
    # )
    # def me(self, request):
    # serializer = CustomUserSerializer(request.user)
    # if request.method == 'PATCH':
    # serializer = CustomUserSerializer(
    # request.user,
    # data=request.data,
    # partial=True
    # )
    # if serializer.is_valid():
    # serializer.validated_data['role'] = request.user.role
    # serializer.save()
    # return Response(serializer.data, status=status.HTTP_200_OK)


class SubscribtionViewSet(viewsets.ModelViewSet):
    queryset = Subscribtion.objects.all()
    serializer_class = SubscribtionSerializer
    # permission_classes = (AdminPermission,)
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ("user", "author")
    search_fields = ("author__username",)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = get_object_or_404(CustomUser, username=self.request.user.username)
        return user.subscriber.all()
