from rest_framework import viewsets
from recipes.models import Tag
from api.serializers.recipes import TagSerializer

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None  # Без пагинации, как в документации
    permission_classes = []  # Доступ открыт всем
