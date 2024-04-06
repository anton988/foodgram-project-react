from django_filters import FilterSet, ModelMultipleChoiceFilter
from .models import Recipe, Tag


class RecipeTagFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ['tags']
