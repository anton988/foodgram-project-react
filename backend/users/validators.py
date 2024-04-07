from django.core.exceptions import ValidationError
from .models import Subscription


def validate_username_include_me(value):
    if value == 'me':
        raise ValidationError(
            "Использовать имя 'me' в качестве username запрещено")
    return value


def validate_subscription(author, subscriber):
    if subscriber.is_anonymous:
        return False, None
    if not author or not subscriber:
        return False, 'Отсутствуют данные об авторе или подписчике'
    if Subscription.objects.filter(
        author=author, subscriber=subscriber
    ).exists():
        return True, 'Вы уже подписаны на данного автора'
    return False, None
