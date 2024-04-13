from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from recipes.models import (
    Tag, Ingredients, Recipe, RecipeIngredients,
    Favorite, Cart
)
from users.serializers import MyUserSerializer
from .validators import is_added_to_list


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = '__all__'


class IngredientsAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=RecipeIngredients.objects.all(),
                fields=['ingredients', 'recipe']
            )
        ]


class IngredientsListingSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class CropRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = MyUserSerializer(read_only=True)
    ingredients = IngredientsListingSerializer(
        many=True,
        source='recipeingredients_recipe'
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError('Должен быть хотя бы один ингредиент')
        ingredients_list = []
        for item in ingredients:
            ingredient_id = get_object_or_404(Ingredients, id=item['id'].id)
            if ingredient_id in ingredients_list:
                raise ValidationError('Ингредиенты не должны повторяться')
            ingredients_list.append(ingredient_id)
        return value

    def validate(self, data):
        required_fields = ['name', 'image', 'text', 'cooking_time']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(
                    f'{field} - поле обязательное для заполнения'
                )
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredients_recipe')
        recipe = Recipe.objects.create(**validated_data)
        RecipeIngredients.objects.filter(recipe=recipe).delete()
        recipe.tags.set(tags)
        RecipeIngredients.objects.bulk_create(
            RecipeIngredients(
                amount=ingredient['amount'],
                ingredients=ingredient['id'],
                recipe=recipe,
            ) for ingredient in ingredients
        )
        return recipe


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = MyUserSerializer(read_only=True)
    ingredients = IngredientsAmountSerializer(
        many=True,
        source='recipeingredients_recipe'
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        return is_added_to_list(
            obj, self.context.get('request').user,
            Favorite
        )

    def get_is_in_shopping_cart(self, obj):
        return is_added_to_list(obj, self.context.get('request').user, Cart)
