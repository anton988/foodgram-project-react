import re
from django.core.exceptions import ValidationError
from .models import Subscription

USERNAME_RE_PATTERN = re.compile(r"^[\w.@+-]+$")


def validate_user(value):
    if value == 'me':
        raise ValidationError(
            'Использовать имя "me" в качестве username запрещено'
        )
    if len(value) > 150:
        raise ValidationError(
            'Длина username не должна превышать 150 символов'
        )
    if not USERNAME_RE_PATTERN.fullmatch(value):
        raise ValidationError(
            'username не должен содержать символы "^[w.@+-]+$"'
        )
    return value


def validate_subscription(author, subscriber):
    if author == subscriber:
        return False
    if subscriber.is_anonymous:
        return False
    if not author or not subscriber:
        return False
    if Subscription.objects.filter(
        author=author, subscriber=subscriber
    ).exists():
        return True
    return False
