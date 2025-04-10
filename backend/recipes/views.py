from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from recipes.models import Recipe


def redirect_short_link(request, short_code):
    """Перенаправление по короткой ссылке на рецепт."""
    recipe = get_object_or_404(Recipe, short_code=short_code)
    recipe_url = reverse('api:recipes-detail', kwargs={'pk': recipe.pk})
    return redirect(recipe_url)
