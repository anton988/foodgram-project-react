from django.db.models import Sum, F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from http import HTTPStatus
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from foodgram.pagination import CustomPagination
from users.permissions import IsOwnerOrReadOnly
from .filters import RecipeFilter, IngredientsFilter
from .models import Tag, Ingredients, Recipe, Favorite, Cart, RecipeIngredients
from .serializers import (
    TagSerializer,
    IngredientsSerializer,
    RecipeSerializer,
    RecipeCreateUpdateSerializer,
    ShortRecipeSerializer
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
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):

        if request.method == 'POST':
            return self.add_obj(Favorite, request.user, pk)

        return self.delete_obj(Favorite, request.user, pk)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):

        if request.method == 'POST':
            return self.add_obj(Cart, request.user, pk)

        return self.delete_obj(Cart, request.user, pk)

    def add_obj(self, model, user, pk):
        recipe_exists = Recipe.objects.filter(id=pk).exists()
        if not recipe_exists:
            return Response(
                {'errors': 'Рецепт не найден'},
                status=HTTPStatus.BAD_REQUEST
            )
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {'errors': 'Рецепт уже добавлен в список'},
                status=HTTPStatus.BAD_REQUEST
            )
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=HTTPStatus.CREATED)

    def delete_obj(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        recipe_exists = Recipe.objects.filter(id=pk).exists()
        if obj.exists():
            obj.delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        elif not recipe_exists:
            return Response(
                {'errors': 'Рецепт не найден'}, status=HTTPStatus.NOT_FOUND
            )
        else:
            return Response(
                {'errors': 'Рецепт не был добавлен в список'},
                status=HTTPStatus.BAD_REQUEST
            )

    @action(methods=['GET'], detail=False,
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        shopping_cart = RecipeIngredients.objects.filter(
            recipe__recipe_in_cart__user=request.user
        ).annotate(
            name=F('ingredients__name'),
            measurement_unit=F('ingredients__measurement_unit')
        ).values('name', 'measurement_unit').annotate(
            total=Sum('amount')
        )
        if shopping_cart:
            shopping_list = 'CПИСОК ПОКУПОК:\n'
            for item in shopping_cart:
                name = item['name']
                total = item['total']
                measurement_unit = item['measurement_unit']
                shopping_list += (
                    f'- {name} - {total} {measurement_unit}\n'
                )
            response = HttpResponse(shopping_list, content_type='text/plain')
            response[
                'Content-Disposition'
            ] = 'attachment; filename="shopping_list.txt"'
            return response
        return Response(
            {'errors': 'Список пуст'}, status=HTTPStatus.BAD_REQUEST
        )
