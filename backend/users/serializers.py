from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from recipes.models import Recipe
from .models import User, Subscription
from .validators import validate_user, validate_subscription


class MyUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def validate_username(self, value):
        return validate_user(value.get('username'))

    def get_is_subscribed(self, obj):
        author = obj
        subscriber = self.context['request'].user
        is_subscribed = validate_subscription(author, subscriber)
        return is_subscribed


class MyUserCreateSerializer(UserCreateSerializer):
    username = serializers.CharField(validators=[validate_user])

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        required_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class ShortRecipeListSerializer(serializers.BaseSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation


class SubscriptionSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        read_only=True
    )
    is_subscribed = serializers.SerializerMethodField(
        read_only=True
    )
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')

    class Meta:
        model = Subscription
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        author = obj.author
        request = self.context.get('request')
        recipes = Recipe.objects.filter(author=author)
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return ShortRecipeListSerializer(recipes, many=True).data

    def get_is_subscribed(self, obj):
        author = obj.author
        subscriber = self.context['request'].user
        is_subscribed = validate_subscription(author, subscriber)
        return is_subscribed

    @staticmethod
    def get_recipes_count(obj):
        subscriber = obj.subscriber
        return Subscription.objects.filter(subscriber=subscriber).count()
