from multiprocessing import context
from django.shortcuts import get_object_or_404
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
        
    def subscribe123(self, request, id):
        subscribing = get_object_or_404(CustomUser, id=id)
        subscriber = request.user

        if request.method == 'POST':
            subscribed = Subscribtion.objects.filter(
                author=subscribing,
                user=subscriber,
            ).exists()
            if subscribed or subscriber == subscribing:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Subscribtion.objects.get_or_create(
                user=subscriber,
                author=subscribing
            )
            serializer = SubscribtionSerializer(
                context=self.get_serializer_context()
            )
            return Response(serializer.to_representation(
                instance=subscribing),
                status=status.HTTP_201_CREATED
            )
    def subscribe123(self, request, id):
        current_user = self.request.user
        print(123)
        if current_user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        author = get_object_or_404(CustomUser, id=id)
        subscribed = (Subscribtion.objects.filter(
                author=author, user=current_user).exists()
            )
        if request.method == "POST":
            # serializer = SubscribtionSerializer(author)
            if subscribed.exists():
                data = {"errors": "Вы уже подписаны на этого автора."}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            author=Subscribtion.objects.create(user=current_user, author=author)
            serializer = SubscribtionSerializer(author,
                context={'request': request})
            return Response(
                # serializer.to_representation(instance=author),
                serializer.data, 
                status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            if not subscribed.exists():
                data = {"errors": "Вы не подписаны на этого автора."}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            subscribed.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    
  # class SubscribtionViewSet(CustomUserViewSet):
    # queryset = Subscribtion.objects.all()
    # queryset = CustomUser.objects.all()
    # serializer_class = SubscribtionSerializer
    # permission_classes = (AdminPermission,)  
    
    
    def subscribe123(self, request, id):
        subscribing = get_object_or_404(CustomUser, id=id)
        subscriber = request.user

        if request.method == 'POST':
            subscribed = Subscribtion.objects.filter(
                author=subscribing,
                user=subscriber,
            ).exists()
            if subscribed or subscriber == subscribing:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Subscribtion.objects.get_or_create(
                user=subscriber,
                author=subscribing
            )
            serializer = SubscribtionSerializer(
                context=self.get_serializer_context()
            )
            return Response(serializer.to_representation(
                instance=subscribing),
                status=status.HTTP_201_CREATED
            )
    
    def subscribe123(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(CustomUser, id=author_id)
        
        if request.method == 'POST':
            serializer = SubscribtionSerializer(author, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            Subscribtion.objects.create(user=user, following=author)
            return Response(serializer.data,
                status=status.HTTP_201_CREATED
            )
        
    def subscribe123(self, request, id):
        followed = get_object_or_404(CustomUser, id=id)
        follower = request.user

        if request.method == 'POST':
            subscribed = (Subscribtion.objects.filter(
                author=followed, user=follower).exists()
            )
            if subscribed is True:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Subscribtion.objects.get_or_create(
                user=follower,
                author=followed
            )
            serializer = SubscribtionSerializer(
                context=self.get_serializer_context()
            )
            return Response(serializer.to_representation(
                instance=followed),
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            Subscribtion.objects.filter(
                user=follower, author=followed
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


    def subscribe123(self, request, id):
        subscribing = get_object_or_404(CustomUser, id=id)
        subscriber = request.user

        if request.method == 'POST':
            subscribed = Subscribtion.objects.filter(
                author=subscribing,
                user=subscriber,
            ).exists()
            if subscribed or subscriber == subscribing:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Subscribtion.objects.get_or_create(
                user=subscriber,
                author=subscribing
            )
            serializer = SubscribtionSerializer(
                context=self.get_serializer_context()
            )
            return Response(serializer.to_representation(
                instance=subscribing),
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            deleted, _ = Subscribtion.objects.filter(
                user=subscriber,
                author=subscribing,
            ).delete()
            if deleted == 0:
                return Response(status=status.HTTP_304_NOT_MODIFIED)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        current_user = request.user
        followed_list = CustomUser.objects.filter(subscribing__user=current_user)
        authors = self.paginate_queryset(followed_list)
        serializer = SubscribtionSerializer(
            authors,
            many=True,
            context={'request':request}
        )
        return self.get_paginated_response(serializer.data)

    # def perform_create(self, serializer):
        # serializer.save(user=self.request.user)

    def get_queryset123(self):
        user = get_object_or_404(CustomUser, username=self.request.user.username)
        return user.subscriber.all()
    
    
    
    

    @action(detail=True, methods=["GET"], url_path="subscriptions")
    def subscriptions123(self, request):
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