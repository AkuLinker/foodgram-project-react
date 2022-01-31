from django.contrib import admin

from recipes.models import Cart, Favorite, Ingredient, Recipe, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', )
    list_filter = ('name', )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name', )
    list_filter = ('name', )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'name', 'author', 'tags_list',
        'ingredients_list', 'favorited'
    )
    search_fields = ('name', 'author', 'tags')
    list_filter = ('name', 'author', 'tags')

    def tags_list(self, obj):
        return '\n'.join([str(tags) for tags in obj.tags.all()])

    def ingredients_list(self, obj):
        return '\n'.join(
            [
                str(ingredients.ingredient)
                for ingredients in obj.ingredient_for_recipe.all()
            ]
        )

    def favorited(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', )
    list_filter = ('user', )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', )
    list_filter = ('user', )
