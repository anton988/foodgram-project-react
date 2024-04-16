from django.core.exceptions import ValidationError
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
        is_subscribed, message = validate_subscription(author, subscriber)
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


class SubscriptionSerializer(MyUserSerializer):
    recipes_count = serializers.IntegerField(read_only=True)
    recipes = ShortRecipeListSerializer(read_only=True, many=True)

    class Meta(MyUserSerializer.Meta):
        fields = MyUserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        author = User.objects.get(pk=data.get('author'))
        subscriber = self.context['request'].user
        is_subscribed, message = validate_subscription(author, subscriber)
        if message:
            raise ValidationError(message)
        return data
