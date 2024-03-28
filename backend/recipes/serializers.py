from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import UserSerializer
from rest_framework import serializers
from recipes.models import (Tag, Ingredients, Recipe, RecipeIngredients,
                            Favorite, Cart)
from users.serializers import UserSerializer

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngridientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = '__all__'


class IngredientsListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class GetIngregientsSerializer(serializers.ModelSerializer):
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


class RecipeListSerializer(serializers.ModelSerializer):
    # ...

    class Meta:
        model = Recipe
        # fields = '__all__'

    # def favorite:

    # def subscribe:


class CreationRecipeSerializer(serializers.ModelSerializer):
    ingredient = IngredientsListSerializer(many=True)
    tag = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                             many=True)
    image = Base64ImageField()
    # name = serializers.ReadOnlyField(source='recipe.name')

    class Meta:
        model = Recipe
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
