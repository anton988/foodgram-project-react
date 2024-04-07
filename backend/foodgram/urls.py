from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from recipes.views import IngredientsViewSet, RecipeViewSet, TagViewSet
from users.views import MyUserViewSet

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', MyUserViewSet, basename='user')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken'))
]
