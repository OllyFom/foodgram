from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.serializers import (
    AvatarSerializer,
    SubscriptionSerializer,
    UserProfileSerializer,
)
from foodgram.constants import MAX_LIMIT_PAGE_SIZE
from users.models import Subscription

User = get_user_model()


class UserPagination(PageNumberPagination):
    """Пагинация пользователей."""
    page_size_query_param = 'limit'
    max_page_size = MAX_LIMIT_PAGE_SIZE


class UserViewSet(DjoserUserViewSet):
    """Вьюсет пользователей на основе Djoser."""
    pagination_class = UserPagination
    permission_classes = [AllowAny]

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        serializer_class=UserProfileSerializer,
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated],
        serializer_class=AvatarSerializer,
    )
    def avatar(self, request):
        user = request.user
        serializer = self.get_serializer(
            user,
            data=request.data,
            context={'request': request},
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
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        pagination_class=UserPagination,
        serializer_class=SubscriptionSerializer,
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(
            subscribers__user=self.request.user
        ).annotate(recipes_count=Count('recipes'))
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            page,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        serializer_class=SubscriptionSerializer,
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(
            User.objects.annotate(recipes_count=Count('recipes')),
            id=id,
        )

        if author == user:
            return Response(
                {'detail': 'Нельзя подписаться на себя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Subscription.objects.filter(user=user, author=author).exists():
            return Response(
                {'detail': 'Вы уже подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Subscription.objects.create(user=user, author=author)
        serializer = self.get_serializer(
            author,
            context={'request': request},
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(
            user=user,
            author=author,
        )

        if not subscription.exists():
            return Response(
                {'detail': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
