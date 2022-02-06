from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, IngredientForRecipe, Recipe, Tag
from users.models import Follow

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.follower.filter(author=obj.id).exists()
        )

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class NewPasswordSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('current_password', 'new_password')

    def validate_new_password(self, value):
        validate_password(value)
        return value


class RecipeFollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )

    def validate(self, data):
        if self.context['request'].user == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return data

    def get_is_subscribed(self, obj):
        return obj.user.follower.filter(author=obj.author).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        queryset = obj.author.recipes.all()
        if request:
            recipes_limit = request.GET.get('recipes_limit')
            if recipes_limit is not None:
                queryset = queryset[:int(recipes_limit)]
        return [RecipeFollowSerializer(item).data for item in queryset]

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'

    def to_internal_value(self, id):
        if not id:
            raise serializers.ValidationError({
                'tags': 'Должен быть как минимум один тег.'
            })
        if not isinstance(id, int):
            raise serializers.ValidationError(
                'Должно быть число')
        return get_object_or_404(Tag, id=id)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientForRecipeSerializer(
        source='ingredient_for_recipe',
        many=True,
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.favorite.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.cart.filter(user=user).exists()

    def validate_tags(self, value):
        tag_list = [tag for tag in value]
        if len(set(tag_list)) < len(tag_list):
            raise serializers.ValidationError(
                'Не может быть два одинаковых тега')
        return value

    @staticmethod
    def create_ingridients(ingredients, recipe):
        for ingredient in ingredients:
            IngredientForRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient['ingredient']['id'],
                amount=ingredient['amount'],
            )

    def create(self, validated_data):
        author = self.context['request'].user
        ingredients = validated_data.pop('ingredient_for_recipe')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingridients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredient_for_recipe')
        tags = validated_data.pop('tags')
        Recipe.objects.filter(id=instance.id).update(**validated_data)
        recipe = get_object_or_404(Recipe, id=instance.id)
        recipe.tags.remove()
        recipe_ingredients = IngredientForRecipe.objects.filter(
            recipe_id=instance.id
            )
        recipe_ingredients.delete()
        self.create_ingridients(ingredients, recipe)
        recipe.tags.set(tags)
        if validated_data.get('image'):
            recipe.image = validated_data.get('image')
            recipe.save()
        return recipe


class RecipeCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
