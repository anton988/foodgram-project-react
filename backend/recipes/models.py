from colorfield.fields import ColorField
from constants import MAX_TAG_LEN, MAX_LEN, LIMIT_VALUE
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from users.models import User


class BaseModel(models.Model):
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        abstract = True


class Tag(models.Model):
    title = models.CharField('Название', max_length=MAX_TAG_LEN, unique=True)
    slug = models.SlugField(
        'Слаг',
        max_length=MAX_TAG_LEN,
        unique=True,
        blank=True
    )
    color = ColorField(
        'Цветовой код',
        format='hex',
        default='#808080',
        unique=True,
        blank=False
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.title


class Ingridients(models.Model):
    title = models.CharField('Название', unique=True)
    measurement_unit = models.CharField('Единицы измерения', unique=True)
    quantity = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                limit_value=LIMIT_VALUE,
                message=(
                    'Колисетво ингридиента не может быть меньше 1.'
                )
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self) -> str:
        return self.title


class Recipes(BaseModel):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes_authors'
    )
    title = models.CharField('Название', max_length=MAX_LEN)
    image = models.ImageField(
        'Картинка',
        upload_to='recipes_images',
        null=True,
        blank=True
    )
    description = models.TextField('Описание')
    ingridients = models.ManyToManyField(
        Ingridients,
        verbose_name='Ингридиенты',
        related_name='recipes_ingridients',
        through='RecipesIngridients',
        null=False,
        blank=False
    )
    tag = models.ManyToManyField(
        Tag,
        verbose_name='Тeг',
        related_name='recipes_tags',
        blank=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(
                limit_value=LIMIT_VALUE,
                message=(
                    'Время приготовления не может быть меньше 1 минуты.'
                )
            )
        ]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.title


class Favorite(BaseModel):
    recipes = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorite_recipes'
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользотель',
        on_delete=models.CASCADE,
        related_name='favorite_users'
    )

    class Meta:
        verbose_name = 'Избранное'
        constraints = UniqueConstraint(fields=['user', 'recipes'],
                                       name='unique_favorite')


class Cart(BaseModel):
    recipes = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='cart'
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользотель',
        on_delete=models.CASCADE,
        related_name='cart'
    )

    class Meta:
        verbose_name = 'Список покупок'
        constraints = UniqueConstraint(fields=['user', 'recipes'],
                                       name='unique_shopping_cart')
