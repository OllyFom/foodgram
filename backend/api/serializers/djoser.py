from django.contrib.auth import get_user_model

from api.serializers.users import UserProfileSerializer

User = get_user_model()


class CustomUserSerializer(UserProfileSerializer):
    """Кастомный сериализатор для отображения юзера через Djoser."""

    class Meta(UserProfileSerializer.Meta):
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'avatar', 'is_subscribed',
        )
