from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers.recipes import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    TagSerializer,
)
from foodgram.constants import MAX_LIMIT_PAGE_SIZE
from recipes.models import Ingredient, Recipe, ShortLink, Tag


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = []


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = []
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipePagination(PageNumberPagination):
    page_size_query_param = 'limit'
    max_page_size = MAX_LIMIT_PAGE_SIZE


def redirect_short_link(request, short_code):
    short_link = get_object_or_404(ShortLink, short_code=short_code)
    recipe_url = reverse('recipes-detail', kwargs={'pk': short_link.recipe.pk})
    return redirect(recipe_url)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = RecipePagination

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthorOrReadOnly()]

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        short_link, _ = ShortLink.objects.get_or_create(recipe=recipe)
        domain = request.build_absolute_uri('/')[:-1]
        short_url = f"{domain}/s/{short_link.short_code}"
        return Response({'short-link': short_url}, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save()
