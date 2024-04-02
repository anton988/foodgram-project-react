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
    name = models.CharField('Название', max_length=MAX_TAG_LEN, unique=True)
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
        return self.name


class Ingredients(models.Model):
    name = models.CharField('Название', unique=True)
    measurement_unit = models.CharField('Единицы измерения', unique=True)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self) -> str:
        return self.name


class Recipe(BaseModel):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipe_author'
    )
    name = models.CharField('Название', max_length=MAX_LEN, blank=False)
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images/',
        null=True,
        blank=True
    )
    text = models.TextField('Описание', blank=False)
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name='Ингредиенты',
        related_name='recipe_ingredients',
        through='RecipeIngredients',
        null=False,
        blank=False
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тeг',
        related_name='recipe_tag',
        blank=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        blank=False,
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
        return self.name


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredients = models.ForeignKey(
        Ingredients,
        verbose_name='Ингридиент',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.PositiveSmallIntegerField(
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
        constraints = (
            models.UniqueConstraint(fields=('recipe', 'ingredients',),
                                    name='unique_recipe_ingredients'),
        )
        verbose_name = 'Количество ингредиентов'


class Favorite(BaseModel):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorite_recipe'
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользотель',
        on_delete=models.CASCADE,
        related_name='favorite_user'
    )

    class Meta:
        verbose_name = 'Избранное'
        constraints = UniqueConstraint(fields=['user', 'recipe'],
                                       name='unique_favorite')


class Cart(BaseModel):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_in_cart'
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользотель',
        on_delete=models.CASCADE,
        related_name='user_cart'
    )

    class Meta:
        verbose_name = 'Список покупок'
        constraints = UniqueConstraint(fields=['user', 'recipe'],
                                       name='unique_cart')
