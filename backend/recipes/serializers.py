from django.core.exceptions import ValidationError
from django.db.models import F
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from recipes.models import (Tag, Ingredients, Recipe, RecipeIngredients,
                            Favorite, Cart)
from users.serializers import MyUserSerializer
from .validators import is_added_to_list, required_field


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


class CropRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для короткого вывода рецептов"""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = MyUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    ingredients = serializers.PrimaryKeyRelatedField(many=True, queryset=Ingredients.objects.all())
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

        def get_ingredients(self, recipe):
            recipe_ingredients = recipe.recipeingredients_recipe.all()
            ingredients_data = []
            for recipe_ingredient in recipe_ingredients:
                ingredient_data = {
                    'id': recipe_ingredient.ingredients.id,
                    'amount': recipe_ingredient.amount
                }
                ingredients_data.append(ingredient_data)
            return ingredients_data

    def get_is_favorited(self, obj):
        return is_added_to_list(
            obj, self.context.get('request').user,
            Favorite
        )

    def get_is_in_shopping_cart(self, obj):
        return is_added_to_list(obj, self.context.get('request').user, Cart)

    def validate_required_fields(self, data):
        required_field(data.get('ingredients'))
        required_field(data.get('name'))
        required_field(data.get('image'))
        required_field(data.get('text'))
        required_field(data.get('cooking_time'))
        return data

    def create_ingredients(self, ingredients, recipe):
        recipe_ingredients = []
        for ingredient, amount in ingredients.values():
            recipe_ingredients.append(RecipeIngredients(
                recipe=recipe,
                ingredients=ingredient,
                amount=amount
            ))
        RecipeIngredients.objects.bulk_create(recipe_ingredients)

    def create_recipe(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context['request'].user
        )
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update_recipe(self, instance, validated_data):
        ingredients = validated_data.get('ingredients', instance.ingredients)
        RecipeIngredients.objects.filter(recipe=instance).delete()
        self.create_ingredients(
            recipe=instance,
            ingredients=ingredients
        )
        instance.tags = validated_data.get('tags', instance.tags)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.save()
        return instance
