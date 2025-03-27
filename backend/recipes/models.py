from django.db import models
from foodgram.constants import TAG_NAME_MAX_LENGTH, COLOR_NAME_MAX_LENGTH

class Tag(models.Model):
    name = models.CharField(
        max_length=TAG_NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Название тега'
    )
    color = models.CharField(
        max_length=COLOR_NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Цвет в HEX (например, #49B64E)'
    )
    slug = models.SlugField(
        max_length=TAG_NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Слаг (уникальный идентификатор)'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=16,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'
