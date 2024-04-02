from django.core.exceptions import ValidationError


def is_added_to_list(obj, user, list_model):
    if user.is_authenticated:
        is_added = list_model.objects.filter(user=user, recipe=obj).exists()
    else:
        is_added = False
    return is_added


def required_field(obj):
    if not obj:
        raise ValidationError('Поле на заполнено')
    return obj
