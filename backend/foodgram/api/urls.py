from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

v1_router = DefaultRouter()
v1_router.register(r'users', UserViewSet, basename='api_users')
v1_router.register(r'tags', TagViewSet, basename='api_tags')
v1_router.register(
    r'ingredients', IngredientViewSet, basename='api_ingredients'
)
v1_router.register(r'recipes', RecipeViewSet, basename='api_recipes')

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'docs/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
]
