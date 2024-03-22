from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.db import models
from django.db.models import UniqueConstraint
from constants import MAX_LEN


class User(AbstractUser):
    email = models.EmailField(
        'Электронная почта',
        max_length=MAX_LEN,
        unique=True,
        validators=[validate_email]
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_LEN,
        unique=True
    )
    first_name = models.CharField('Имя', max_length=MAX_LEN)
    last_name = models.CharField('Фамилия', max_length=MAX_LEN)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='author'
    )
    subscriber = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='subscribtion'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = UniqueConstraint(fields=['author', 'subscriber'],
                                       name='unique_subscription')
