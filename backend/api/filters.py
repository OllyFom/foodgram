from typing import Any

from django.db.models import QuerySet

from django_filters.rest_framework import (
    AllValuesMultipleFilter,
    BooleanFilter,
    CharFilter,
    FilterSet,
    NumberFilter,
)

from recipes.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    """Фильтр для поиска ингредиентов."""

    name = CharFilter(
        field_name='name',
        lookup_expr='istartswith',
        help_text='Название ингредиента (по начальным буквам)'
    )

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    """Фильтр для рецептов."""
    tags = AllValuesMultipleFilter(
        field_name='tags__slug',
        help_text='Фильтрация по слагам тегов'
    )
    author = NumberFilter(
        field_name='author__id',
        help_text='ID автора рецепта'
    )
    is_favorited = BooleanFilter(
        method='filter_is_favorited',
        help_text='Фильтр по избранному'
    )
    is_in_shopping_cart = BooleanFilter(
        method='filter_is_in_cart',
        help_text='Фильтр по корзине'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(
        self,
        queryset: QuerySet,
        name: str,
        value: Any
    ) -> QuerySet:
        """Фильтрация рецептов по избранному."""
        user = self.request.user
        if user.is_anonymous:
            return queryset.none()
        if value:
            return queryset.filter(favorited_by__user=user)
        return queryset.exclude(favorited_by__user=user)

    def filter_is_in_cart(
        self,
        queryset: QuerySet,
        name: str,
        value: Any
    ) -> QuerySet:
        """Фильтрация рецептов по наличию покупок."""
        user = self.request.user
        if user.is_anonymous:
            return queryset.none()
        if value:
            return queryset.filter(in_carts__user=user)
        return queryset.exclude(in_carts__user=user)
