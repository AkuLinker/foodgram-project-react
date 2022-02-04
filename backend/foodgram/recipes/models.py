from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):

    name = models.CharField(
        max_length=150,
        verbose_name='название',
    )
    color = models.CharField(
        max_length=7,
        verbose_name='цвет',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='слаг',
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        ordering = ['id']

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(
        max_length=150,
        verbose_name='название',
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='единица измерения',
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        ordering = ['id']

    def __str__(self):
        return self.name


class Recipe(models.Model):

    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='теги',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='автор',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='ингредиенты',
    )
    name = models.CharField(
        max_length=150,
        verbose_name='название',
    )
    image = models.ImageField(
        upload_to='recipes/',
        null=True,
        blank=True,
        verbose_name='картинка',
    )
    text = models.TextField(verbose_name='описание', )
    cooking_time = models.IntegerField(
        validators=(MinValueValidator(
            1, 'Время приготовления не может быть меньше одной минуты.'
        ),),
        verbose_name='время приготовления в минутах',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации'
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ('-pub_date', )


class IngredientForRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_for_recipe',
        verbose_name='рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_for_recipe',
        verbose_name='ингредиент',
    )
    amount = models.PositiveIntegerField(
        default=1,
        validators=(
            MinValueValidator(
                1, 'Amount can\'t be less than 1'
            ),
        ),
        verbose_name='количество',
    )

    class Meta:
        verbose_name = 'ингредиент для рецепта'
        verbose_name_plural = 'ингредиенты для рецепта'
        ordering = ['id']
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
        verbose_name='пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='рецепт',
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'избранные'
        ordering = ['id']
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
        verbose_name='пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='рецепт',
    )

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'корзины'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                name='unique_cart',
                fields=('user', 'recipe'),
            )
        ]
