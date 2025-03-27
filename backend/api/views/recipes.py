from rest_framework import viewsets, filters
from recipes.models import Tag, Ingredient
from api.serializers.recipes import TagSerializer, IngredientSerializer
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import IngredientFilter

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None  # Без пагинации, как в док
    permission_classes = []  # Доступ открыт всем


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = []
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
