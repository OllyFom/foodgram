from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Count

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from djoser.views import UserViewSet as DjoserUserViewSet
from api.serializers import (
    AvatarSerializer,
    SubscriptionSerializer,
    UserProfileSerializer,
)
from api.serializers.djoser import CustomUserCreateSerializer
from foodgram.constants import MAX_LIMIT_PAGE_SIZE
from users.models import Subscription

User = get_user_model()


class UserPagination(PageNumberPagination):
    """Пагинация пользователей."""
    page_size_query_param = 'limit'
    max_page_size = MAX_LIMIT_PAGE_SIZE


class CustomUserViewSet(DjoserUserViewSet):
    """Кастомный вьюсет пользователей на основе Djoser."""
    pagination_class = UserPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = User.objects.all()
        if self.action in ('subscriptions', 'subscribe'):
            queryset = queryset.annotate(recipes_count=Count('recipes'))
            if self.action == 'subscriptions':
                user = self.request.user
                if user.is_authenticated:
                    queryset = queryset.filter(subscribers__user=user)
                else:
                    queryset = queryset.none()
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        if self.action == 'me':
            return UserProfileSerializer
        if self.action == 'avatar':
            return AvatarSerializer
        if self.action in ('subscriptions', 'subscribe'):
            return SubscriptionSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            page if page is not None else queryset,
            many=True,
            context={'request': request}
        )
        return (
            self.get_paginated_response(serializer.data)
            if page is not None else Response(serializer.data)
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request):
        user = request.user
        serializer = AvatarSerializer(
            user,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        user = request.user
        if not user.avatar:
            return Response(
                {'detail': 'Аватар не установлен.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        pagination_class=UserPagination
    )
    def subscriptions(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page if page is not None else queryset,
            many=True,
            context={'request': request}
        )
        return (
            self.get_paginated_response(serializer.data)
            if page is not None else Response(serializer.data)
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(self.get_queryset(), id=id)

        if author == user:
            return Response(
                {'detail': 'Нельзя подписаться на себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Subscription.objects.filter(user=user, author=author).exists():
            return Response(
                {'detail': 'Вы уже подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Subscription.objects.create(user=user, author=author)
        serializer = SubscriptionSerializer(
            author,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(user=user, author=author)

        if not subscription.exists():
            return Response(
                {'detail': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
