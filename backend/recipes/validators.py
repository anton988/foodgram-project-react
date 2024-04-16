from django.core.exceptions import ValidationError
from .models import Recipe


def is_added_to_list(obj, user, list_model):
    if user.is_authenticated:
        recipe_exists = Recipe.objects.filter(id=obj.id).exists()
        if recipe_exists:
            is_added = list_model.objects.filter(
                user=user, recipe=obj
            ).exists()
        else:
            raise ValidationError("Рецепт не существует")
    else:
        is_added = False
    return is_added
