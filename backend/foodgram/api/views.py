from django.db.models import Sum
from django.http.response import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Cart, Favorite, Ingredient, IngredientForRecipe,
                            Recipe, Tag)
from users.models import Follow, User
from api.filters import SpecialIngredientFilter, SpecialRecipeFilter
from api.pagination import CustomPageNumberPagination
from api.permissions import SafeOrAuthenticatedAndAuthorPermission
from api.serializers import (CustomUserSerializer, FollowSerializer,
                             IngredientSerializer, NewPasswordSerializer,
                             RecipeCartSerializer, RecipeFollowSerializer,
                             RecipeSerializer, TagSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPageNumberPagination
    http_method_names = ['get', 'post', 'delete']
    permission_classes = [AllowAny]

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def set_password(self, request):
        serializer = NewPasswordSerializer(data=request.data)
        user = request.user
        if serializer.is_valid():
            print(request.data)
            if not user.check_password(request.data.get('current_password')):
                return Response(
                    {'current_password': ['Wrong password.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(request.data.get('new_password'))
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        user = request.user
        subscriptions = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(subscriptions)
        serializer = FollowSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(User, id=pk)
        subscription = user.follower.filter(author=author)
        if request.method == 'POST':
            if subscription.exists() or author == user:
                return Response(
                    {
                        'errors': (
                            'you\'re already subscribed to this user '
                            'or you\'re trying to subscribe to yourself.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            new_subscription = Follow.objects.create(
                user=user, author=author
            )
            serializer = FollowSerializer(new_subscription)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if subscription.exists():
            subscription.delete()
            return Response(
                {
                    'success': 'you\'re successfully unsubscribed from user'
                },
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
                    {
                        'errors': 'you\'ve no subscription to this user'
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SpecialIngredientFilter
    filterset_fields = ('name', )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SpecialRecipeFilter
    pagination_class = CustomPageNumberPagination
    permission_classes = (SafeOrAuthenticatedAndAuthorPermission, )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = self.request.user.favorite.filter(recipe=recipe)
        if request.method == 'POST':
            if favorite.exists():
                return Response(
                    {
                        'errors': 'The recipe is already in your favorite list'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite = Favorite.objects.create(
                user=self.request.user, recipe=recipe
            )
            favorite.save()
            serializer = RecipeFollowSerializer(recipe)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        if not favorite.exists():
            return Response(
                {
                    'errors': 'The recipe is not in your favorite list'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        favorite.delete()
        return Response(
            {
                'success': 'The recipe successfully deleted from favorite list'
            },
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        cart = self.request.user.cart.filter(recipe=recipe)
        if request.method == 'POST':
            if cart.exists():
                return Response(
                    {
                        'errors': 'The recipe is already in your cart'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart = Cart.objects.create(
                user=self.request.user, recipe=recipe
            )
            cart.save()
            serializer = RecipeCartSerializer(recipe)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        if not cart.exists():
            return Response(
                {
                    'errors': 'The recipe is not in your cart'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart.delete()
        return Response(
            {
                'success': 'The recipe successfully deleted from cart'
            },
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        text = 'List of ingredients for your recipes:\n\n'
        ingredients = IngredientForRecipe.objects.filter(
            recipe__cart__user=request.user
        ).values('ingredient__name', 'ingredient__measurement_unit').annotate(
            amount=Sum("amount")
        )

        text += '\n'.join([
            f'{ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]}) — '
            f'{ingredient["amount"]}\n' for ingredient in ingredients
        ])
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response
