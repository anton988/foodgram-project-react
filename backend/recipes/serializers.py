from django.core.exceptions import ObjectDoesNotExist, ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from recipes.models import (Tag, Ingredients, Recipe, RecipeIngredients,
                            Favorite, Cart)
from users.serializers import UserSerializer
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
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class GetIngregientsAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = GetIngregientsAmountSerializer(
        many=True,
        source='recipe_ingredients'
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

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


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientsAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'ingredients', 'tags', 'image', 'name', 'text',
            'cooking_time', 'author'
        )

    def validate_required_fields(self, data):
        required_field(data.get('ingredients'))
        required_field(data.get('name'))
        required_field(data.get('text'))
        required_field(data.get('cooking_time'))
        return data

    def validate_tags(self, value):
        if len(set(value)) != len(value):
            raise ValidationError('Такой тег уже есть')
        return value

    def create_recipe_ingredients(self, recipe, ingredients):
        recipe_ingredients = []
        for ingredient_data in ingredients:
            ingredient = Ingredients.objects.get(pk=ingredient_data['id'])
            amount = ingredient_data['amount']
            recipe_ingredients.append(RecipeIngredients(
                recipe=recipe,
                ingredient=ingredient,
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
        self.create_recipes_ingredients(recipe, ingredients)
        return recipe

    def update_recipe(self, instance, validated_data):
        ingredients = validated_data.get('ingredients', instance.ingredients)
        RecipeIngredients.objects.filter(recipe=instance).delete()
        self.create_recipe_ingredients(
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

    def validate(self, recipe):
        return RecipeSerializer(recipe, context=self.context).data
