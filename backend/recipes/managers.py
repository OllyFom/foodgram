from django.db.models import Exists, Manager, OuterRef


class RecipeManager(Manager):
    """Менеджер для модели рецептов."""
    def with_user_annotations(self, user):
        from recipes.user_recipe_models import (  # Для искл. цикл. ошибки
            Favorite,
            ShoppingCart,
        )

        if not user.is_authenticated:
            return self.get_queryset().annotate(
                is_favorited=Exists(Favorite.objects.none()),
                is_in_shopping_cart=Exists(ShoppingCart.objects.none()),
            )

        favorite_subquery = Favorite.objects.filter(
            user=user,
            recipe=OuterRef('pk'),
        )
        cart_subquery = ShoppingCart.objects.filter(
            user=user,
            recipe=OuterRef('pk'),
        )
        return self.get_queryset().annotate(
            is_favorited=Exists(favorite_subquery),
            is_in_shopping_cart=Exists(cart_subquery),
        )
