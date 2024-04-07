from django_filters import FilterSet, ModelMultipleChoiceFilter, CharFilter
from .models import Tag, Ingredients, Recipe


class RecipeTagFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ['tags']


class IngredientsFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredients
        fields = ['name']
