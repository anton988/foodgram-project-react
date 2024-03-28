from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import Subscription


def validate_username_include_me(value):
    if value == 'me':
        raise serializers.ValidationError(
            "Использовать имя 'me' в качестве username запрещено")
    return value


def validate_subscription(author, subscriber):
    if not author or not subscriber:
        raise ValidationError('Отсутствуют данные об авторе или подписчике.')
    if Subscription.objects.filter(
        author=author, subscriber=subscriber
    ).exists():
        raise ValidationError('Вы уже подписаны на данного автора.')
    if author == subscriber:
        raise ValidationError('Вы не можете подписаться на самого себя.')