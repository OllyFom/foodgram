from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.users import UserViewSet
from api.views.recipes import TagViewSet, IngredientViewSet, RecipeViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
]
