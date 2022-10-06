from multiprocessing import context
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
from users.permissions import AdminPermission
from users.serializers import (
    CustomUserSerializer,
    RegistrationSerializer,
    SubscribtionSerializer,
    SubscriptionsSerializer
)
# from recipes.serializers import SubscriptionsSerializer


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
    # permission_classes = (AllowAny,)
    # lookup_field = "username"
    # pagination_class = None
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ("user", "author")
    search_fields = ("author__username",)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(CustomUser, id=pk)
        if request.method == 'POST':
            data = {'user': user.id, 'author': pk}
            serializer = SubscribtionSerializer(
                data=data,
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        follow = Subscribtion.objects.filter(user=user, author=author)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Вы не подписаны на этого автора'},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        current_user = request.user
        queryset = CustomUser.objects.filter(subscribing__user=current_user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            pages,
            many=True,
            context={'request':request}
        )
        return self.get_paginated_response(serializer.data)
    
    
    # @action(detail=True, methods=["GET"])
    def subscriptions123(self, request, pk):
        current_user = self.request.user
        print(current_user)
        if current_user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        author = get_object_or_404(CustomUser, pk=pk)
        subscriptions_list = SubscribtionSerializer.objects.filter(author__user=current_user)
        paginator = PageNumberPagination()
        paginator.page_size_query_param = 'limit'
        authors = paginator.paginate_queryset(subscriptions_list, request=request)
        serializer = ListSerializer(
            child=SubscribtionSerializer(),
            context=self.get_serializer_context())
        return paginator.get_paginated_response(serializer.to_representation(authors))