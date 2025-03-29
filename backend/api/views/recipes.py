from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.http import HttpResponse
from recipes.models import RecipeIngredient

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers.recipes import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    TagSerializer,
)
from foodgram.constants import MAX_LIMIT_PAGE_SIZE
from recipes.models import Ingredient, Recipe, ShortLink, Tag, ShoppingCart

from api.serializers.recipes import RecipeMiniSerializer


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
        if self.action in ('create', 'shopping_cart', 'remove_from_cart', 'download_shopping_cart'):
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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response({'detail': 'Рецепт уже в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.create(user=user, recipe=recipe)
        serializer = RecipeMiniSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def remove_from_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        cart_item = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if cart_item.exists():
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Рецепта нет в списке покупок.'},
                        status=status.HTTP_400_BAD_REQUEST)
    
    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = request.user
        recipes = user.cart.values_list('recipe', flat=True)

        ingredients = RecipeIngredient.objects.filter(
            recipe__in=recipes
        ).select_related('ingredient')

        summary = {}
        for item in ingredients:
            name = item.ingredient.name
            unit = item.ingredient.measurement_unit
            amount = item.amount
            key = (name, unit)
            if key in summary:
                summary[key] += amount
            else:
                summary[key] = amount

        lines = []
        for (name, unit), amount in summary.items():
            lines.append(f'{name} ({unit}) — {amount}')
        content = '\n'.join(lines)

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response