from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import (
    viewsets, mixins, permissions, status
)
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers.users import (
    UserProfileSerializer,
    CreateUserProfileSerializer,
    AvatarSerializer,
    SetPasswordSerializer,
    SubscriptionSerializer
)
from foodgram.constants import MAX_LIMIT_PAGE_SIZE
from users.models import Subscription

User = get_user_model()


class UserPagination(PageNumberPagination):
    """Пагинация пользователей."""
    page_size_query_param = 'limit'
    max_page_size = MAX_LIMIT_PAGE_SIZE


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Вьюсет пользователей."""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    pagination_class = UserPagination

    def get_serializer_class(self):
        if self.action == 'me':
            return UserProfileSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.action == 'avatar':
            return AvatarSerializer
        if self.action == 'create':
            return CreateUserProfileSerializer
        if self.action in ('subscriptions', 'subscribe'):
            return SubscriptionSerializer
        return UserProfileSerializer

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
            partial=True,
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
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        current_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(current_password):
            return Response(
                {'current_password': 'Неверный текущий пароль.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        pagination_class=UserPagination
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribers__user=request.user)
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
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, pk=pk)

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
    def unsubscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, pk=pk)
        subscription = Subscription.objects.filter(user=user, author=author)

        if not subscription.exists():
            return Response(
                {'detail': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
