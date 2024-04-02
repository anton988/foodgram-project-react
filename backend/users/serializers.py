from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from recipes.models import Recipe
from .models import Subscription
from .validators import validate_username_include_me, validate_subscription

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id',
                  'email',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed')

    def validate_username(self, value):
        return validate_username_include_me(value.get('username'))

    def get_is_subscribed(self, obj):
        author = obj
        subscriber = self.context['request'].user
        is_subscribed, message = validate_subscription(author, subscriber)
        if message:
            raise ValidationError(message)
        return is_subscribed


class CreateUserSerializer(UserCreateSerializer):
    username = serializers.CharField(validate_username_include_me)

    class Meta:
        model = User
        fields = ('email',
                  'username',
                  'first_name',
                  'last_name',
                  'password')


class SubscriptionListSerializer(serializers.BaseSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(UserSerializer):
    recipes_count = serializers.IntegerField(read_only=True)
    recipes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        all_recipes = obj.recipes.all()
        if limit:
            try:
                limit = int(limit)
                all_recipes = all_recipes[:limit]
            except ValueError:
                pass
        recipes_dic = SubscriptionListSerializer(
            all_recipes,
            many=True,
            read_only=True
        )
        return recipes_dic.data


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('author', 'subscriber')

    def validate(self, data):
        author = data.get('author')
        subscriber = self.context['request'].user
        is_valid, message = validate_subscription(author, subscriber)
        if message:
            raise ValidationError(message)
        return data
