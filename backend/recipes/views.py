from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from recipes.models import ShortLink


def redirect_short_link(request, short_code):
    """Перенаправление по короткой ссылке на рецепт."""
    short_link = get_object_or_404(ShortLink, short_code=short_code)
    recipe_url = reverse(
        'api:recipes-detail',
        kwargs={'pk': short_link.recipe.pk},
    )
    return redirect(recipe_url)
