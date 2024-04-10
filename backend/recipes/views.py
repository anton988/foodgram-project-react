import datetime as dt
from http import HTTPStatus
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly, SAFE_METHODS
)

from rest_framework.response import Response
from foodgram.pagination import CustomPagination
from users.models import User
from users.permissions import IsOwnerOrReadOnly
from .filters import RecipeTagFilter, IngredientsFilter
from .models import Tag, Ingredients, Recipe, Favorite, Cart, RecipeIngredients
from .serializers import (
    TagSerializer,
    IngredientsSerializer,
    RecipeSerializer,
    CropRecipeSerializer
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientsFilter
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filterset_class = RecipeTagFilter
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавить удалить в избранное"""

        if request.method == 'POST':
            return self.add_obj(Favorite, request.user, pk)

        return self.delete_obj(Favorite, request.user, pk)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Добавить удалить в корзину"""

        if request.method == 'POST':
            return self.add_obj(Cart, request.user, pk)

        return self.delete_obj(Cart, request.user, pk)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Скачать список ингредиентов"""

        user = request.user
        if not user.cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = RecipeIngredients.objects.filter(
            recipe__cart__user=request.user
        ).values(
            'ingredients__name',
            'ingredients__measurement_unit'
        ).annotate(amount=Sum('amount'))
        today = dt.datetime.today()
        shopping_list = (
            f'Список покупок для: {user.get_full_name()}\n\n'
            f'Дата: {today:%Y-%m-%d}\n\n'
        )
        shopping_list += '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        shopping_list += f'\n\nFoodgram ({today:%Y})'

        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response

    def add_obj(self, model, user, pk):
        """добавить обьект"""

        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({
                'errors': 'Рецепт уже добавлен в список'
            }, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = CropRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_obj(self, model, user, pk):
        """Удалить обьект"""

        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({
            'errors': 'Рецепт уже удален'
        }, status=status.HTTP_400_BAD_REQUEST)
