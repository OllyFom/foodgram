from django.db.transaction import atomic

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.serializers.users import UserProfileSerializer
from foodgram.constants import (
    COOKING_TIME_MAX,
    COOKING_TIME_MIN,
    INGREDIENT_MAX_AMOUNT,
    INGREDIENT_MIN_AMOUNT,
    RECIPE_NAME_MAX_LENGTH,
)
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента с количеством."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def validate_amount(self, value):
        if value < INGREDIENT_MIN_AMOUNT or value > INGREDIENT_MAX_AMOUNT:
            raise serializers.ValidationError(
                f'Количество ингредиента должно быть от '
                f'{INGREDIENT_MIN_AMOUNT} до {INGREDIENT_MAX_AMOUNT}.'
            )
        return value


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта на чтение."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserProfileSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(many=True, read_only=True)
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_image(self, obj):
        return obj.image.url if obj.image else None


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта на запись."""

    ingredients = IngredientAmountSerializer(
        many=True,
        write_only=True,
        allow_empty=False,
        required=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
        allow_empty=False,
        required=True,
    )
    image = Base64ImageField(required=True)
    name = serializers.CharField(max_length=RECIPE_NAME_MAX_LENGTH)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        if 'ingredients' not in data:
            raise serializers.ValidationError({
                'ingredients': (
                    'Поле "ingredients" обязательно. '
                    'Укажите хотя бы один ингредиент.'
                ),
            })
        if 'tags' not in data:
            raise serializers.ValidationError({
                'tags': (
                    'Поле "tags" обязательно. Укажите хотя бы один тег.'
                ),
            })

        ingredients = data['ingredients']
        tags = data['tags']

        if len(tags) != len(set(tag.id for tag in tags)):
            raise serializers.ValidationError({
                'tags': 'Теги не должны повторяться.',
            })

        seen = set()
        for item in ingredients:
            ingredient_id = item['ingredient'].id
            if ingredient_id in seen:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиенты не должны повторяться.',
                })
            seen.add(ingredient_id)

        return data

    def validate_cooking_time(self, value):
        if value < COOKING_TIME_MIN or value > COOKING_TIME_MAX:
            raise serializers.ValidationError(
                f'Время приготовления должно быть от {COOKING_TIME_MIN} до '
                f'{COOKING_TIME_MAX} минут.'
            )
        return value

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError('Наличие картинки обязательно.')
        return value

    def create_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['ingredient'],
                amount=item['amount'],
            )
            for item in ingredients_data
        ])

    @atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        user = self.context['request'].user
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.tags.set(tags)
        instance.ingredients.all().delete()
        self.create_ingredients(instance, ingredients)
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data
