from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):

    name = models.CharField(
        max_length=150,
        verbose_name='Tag\'s name',
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Tag\'s color',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Tag\'s slug',
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(
        max_length=150,
        verbose_name='Ingredient\'s name',
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Ingredient\'s measurement unit',
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):

    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Tag',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Author',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ingredient',
    )
    name = models.CharField(
        max_length=150,
        verbose_name='Recipe\'s name',
    )
    image = models.ImageField(
        upload_to='recipes/',
        null=True,
        blank=True,
        verbose_name='Recipe\'s image',
    )
    text = models.TextField(verbose_name='Recipe\'s text', )
    cooking_time = models.IntegerField(
        validators=(MinValueValidator(
            1, 'Time of cooking can\'t be less then 1 minute.'
        ),),
        verbose_name='Cooking time in minutes',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Publication date'
    )

    class Meta:
        ordering = ('-pub_date', )


class IngredientForRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_for_recipe',
        verbose_name='Recipe',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_for_recipe',
        verbose_name='Ingredient',
    )
    amount = models.PositiveIntegerField(
        default=1,
        validators=(
            MinValueValidator(
                1, 'Amount can\'t be less than 1'
            ),
        ),
        verbose_name='Ingredient\'s amount',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='Unique_ingredient_for_recipe',
                fields=('recipe', 'ingredient'),
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='User',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Recipe',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_favorite',
                fields=('user', 'recipe'),
            )
        ]


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='User',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Recipe',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_cart',
                fields=('user', 'recipe'),
            )
        ]
