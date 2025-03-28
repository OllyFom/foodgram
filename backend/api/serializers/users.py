from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import password_validation, get_user_model
from django.contrib.auth.password_validation import validate_password
from api.serializers.recipe_mini import RecipeMiniSerializer

from foodgram.constants import (
    EMAIL_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
    NAME_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    USERNAME_REGEX,
)

User = get_user_model()


class CreateUserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        required=True
    )
    username = serializers.RegexField(
        regex=USERNAME_REGEX.regex,
        max_length=USERNAME_MAX_LENGTH,
        required=True
    )
    first_name = serializers.CharField(
        max_length=NAME_MAX_LENGTH,
        required=True
    )
    last_name = serializers.CharField(
        max_length=NAME_MAX_LENGTH,
        required=True
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=PASSWORD_MIN_LENGTH,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password'
        )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                f'Пользователь с эл. адресом "{value}" уже существует.'
            )
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                f'Пользователь с ником "{value}" уже существует, придумайте новый.'
            )
        return value

    def validate_password(self, value):
        validate_password(value, self.instance)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'avatar', 'is_subscribed'
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.subscribers.filter(user=user).exists()


class AvatarSerializer(serializers.Serializer):
    avatar = serializers.ImageField(required=True)

    def update(self, instance, validated_data):
        instance.avatar = validated_data['avatar']
        instance.save()
        return instance


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value, self.context['request'].user)
        return value


class SubscriptionSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'avatar', 'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return user.subscriptions.filter(author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        queryset = obj.recipes.all()
        if limit and limit.isdigit():
            queryset = queryset[:int(limit)]
        return RecipeMiniSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
