import datetime as dt
from http import HTTPStatus
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly, SAFE_METHODS
)

from rest_framework.response import Response
from foodgram.pagination import CustomPagination
from users.models import User
from users.permissions import IsOwnerOrReadOnly
from users.serializers import SubscriptionListSerializer
from .filters import RecipeTagFilter, IngredientsFilter
from .models import Tag, Ingredients, Recipe, Favorite, Cart, RecipeIngredients
from .serializers import (
    TagSerializer,
    IngredientsSerializer,
    RecipeSerializer,
    CreateRecipeSerializer
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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.user.is_authenticated:
            context['subscriptions'] = set(
                Favorite.objects
                .filter(user=self.request.user)
                .values_list('recipe__author_id', flat=True)
            )
            context['is_in_shopping_cart'] = set(
                Cart.objects
                .filter(user=self.request.user)
                .values_list('recipe_id', flat=True)
            )
        return context

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return CreateRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, pk):
        if self.request.method == 'POST':
            return self.add_to(Cart, self.request.user, id=pk)
        return self.delete_from(Cart, self.request.user, id=pk)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, pk):
        if self.request.method == 'POST':
            return self.add_to(Favorite, self.request.user, id=pk)
        return self.delete_from(Favorite, self.request.user, id=pk)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        if not request.user.shopping_cart.exists():
            return Response(status=HTTPStatus.NOT_FOUND)
        ingredients = RecipeIngredients.objects.filter(
            recipe__recipe_in_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        today = dt.date.today()
        title = f'Foodgram: {today}\n\n'
        shopping_list = title + '\n'.join(
            [
                f'- {ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]})'
                f' - {ingredient["amount"]}'
                for ingredient in ingredients
            ]
        )

        filename = f'{today}-shopping-list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @staticmethod
    def add_to(model, user, pk: int):
        if model.objects.filter(recipe_id=pk, user=user).exists():
            return Response(
                {'errors': 'Рецепт уже был добавлен'},
                status=HTTPStatus.BAD_REQUEST
            )
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(recipe=recipe, user=user)
        serializer = SubscriptionListSerializer(recipe)
        return Response(serializer.data, status=HTTPStatus.CREATED)

    @staticmethod
    def delete_from(model, user: User, pk: int):
        obj = model.objects.filter(recipe_id=pk, user=user)
        if obj.exists():
            obj.delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(
            {'error': 'Рецепт не существует или был удален'},
            status=HTTPStatus.BAD_REQUEST
        )
