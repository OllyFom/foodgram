from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.users import UserViewSet
from api.views.recipes import TagViewSet, IngredientViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
]
