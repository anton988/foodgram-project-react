from django.core.exceptions import ValidationError
from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from recipes.models import Recipe
from .models import User, Subscription
from .validators import validate_username_include_me, validate_subscription


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
        return validate_username_include_me(value.get('username'))

    def get_is_subscribed(self, obj):
        author = obj
        subscriber = self.context['request'].user
        is_subscribed, message = validate_subscription(author, subscriber)
        return is_subscribed


class MyUserCreateSerializer(UserCreateSerializer):
    username = serializers.CharField(validators=[validate_username_include_me])

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


class SubscriptionListSerializer(serializers.BaseSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation


class SubscriptionSerializer(UserSerializer):
    recipes_count = serializers.IntegerField(read_only=True)
    recipes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )

    def get_recipes(self, obj):
        user = obj
        queryset = Recipe.objects.filter(author=user)
        limit = self.context['request'].query_params.get('recipes_limit')
        if limit:
            queryset = queryset[:int(limit)]
        serializer = SubscriptionListSerializer(
            queryset, many=True,
            context=self.context
        )
        return serializer.data


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('author', 'subscriber')

    def validate(self, data):
        author = data.get('author')
        subscriber = self.context['request'].user
        bool, message = validate_subscription(author, subscriber)
        if message:
            raise ValidationError(message)
        return data
