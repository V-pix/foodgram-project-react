from django.shortcuts import get_object_or_404, get_list_or_404
from djoser.views import UserViewSet
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import ListSerializer

from users.models import CustomUser, Subscribtion
from recipes.serializers import (
    CustomUserSerializer,
    RegistrationSerializer,
    SubscribtionSerializer,
    SubscriptionsSerializer,
)


class UserRegistrationView(APIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            username = request.data.get("username")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ("user", "author")
    search_fields = ("author__username",)

    @action(
        detail=True, methods=["POST", "DELETE"], permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(CustomUser, id=pk)
        if request.method == "POST":
            data = {"user": user.id, "author": pk}
            serializer = SubscribtionSerializer(
                data=data,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        follow = Subscribtion.objects.filter(user=user, author=author)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "Вы не подписаны на этого автора"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        current_user = request.user
        if current_user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        queryset = CustomUser.objects.filter(subscribing__user=current_user)
        paginator = PageNumberPagination()
        paginator.page_size_query_param = "limit"
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)
