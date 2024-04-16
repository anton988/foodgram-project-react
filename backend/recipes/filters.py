from django_filters import (
    FilterSet, ModelMultipleChoiceFilter, CharFilter,
    ModelChoiceFilter, Filter
)
from .models import Tag, Ingredients, Recipe
from users.models import User


class CustomBooleanFilter(Filter):
    def filter(self, qs, value):
        if value in (True, '1'):
            return qs.filter(**{self.field_name: True})
        elif value in (False, '0'):
            return qs.filter(**{self.field_name: False})
        return qs


class RecipeFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = CustomBooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = CustomBooleanFilter(method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite_recipe__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(recipe_in_cart__user=self.request.user)
        return queryset


class IngredientsFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredients
        fields = ('name',)
