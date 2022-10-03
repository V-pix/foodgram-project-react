from django.shortcuts import get_object_or_404
# from djoser.views import UserViewSet
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import ListSerializer

from users.models import CustomUser, Subscribtion
from users.permissions import AdminPermission
from users.serializers import (
    CustomUserSerializer,
    ObtainTokenSerializer,
    RegistrationSerializer,
    SubscribtionSerializer,
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
            # confirmation_generator(username)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    # permission_classes = (AdminPermission,)
    permission_classes = (AllowAny,)
    lookup_field = "username"
    # pagination_class = None


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
    
    @action(detail=True, methods=["POST", "DELETE"])
    def subscribe(self, request, pk):
        current_user = self.request.user
        if current_user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        author = get_object_or_404(CustomUser, pk=pk)
        subscribed = (Subscribtion.objects.filter(
                author=author, user=current_user).exists()
            )
        if request.method == "POST":
            serializer = SubscribtionSerializer(author)
            if subscribed.exists():
                data = {"errors": "Вы уже подписаны на этого автора."}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            Subscribtion.objects.create(user=current_user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            if not subscribed.exists():
                data = {"errors": "Вы не подписаны на этого автора."}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            subscribed.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["GET"], url_path="subscriptions")
    def subscriptions(self, request):
        current_user = request.user
        queryset = Subscribtion.objects.filter(user=current_user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribtionSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
    
    # def subscriptions(self, request, pk):
        # current_user = self.request.user
        # if current_user.is_anonymous:
            # return Response(status=status.HTTP_401_UNAUTHORIZED)
        # author = get_object_or_404(CustomUser, pk=pk)
        # subscriptions_list = SubscribtionSerializer.objects.filter(author__user=current_user)
        # paginator = PageNumberPagination()
        # paginator.page_size_query_param = 'limit'
        # authors = paginator.paginate_queryset(subscriptions_list, request=request)
        # serializer = ListSerializer(
            # child=SubscribtionSerializer(),
            # context=self.get_serializer_context())
        # return paginator.get_paginated_response(serializer.to_representation(authors))
        

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
