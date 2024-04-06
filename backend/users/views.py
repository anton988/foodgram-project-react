from http import HTTPStatus
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import User, Subscription
from .serializers import MyUserSerializer, SubscriptionSerializer


class MyUserViewSet(UserViewSet):
    serializer_class = MyUserSerializer
    pagination_class = PageNumberPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.user.is_authenticated:
            context['is_subscribed'] = set(
                Subscription.objects.filter(user=self.request.user)
                .values_list('author_id')
            )
            context['recipes_count'] = self.request.user.recipes.count()
        return context

    def me(self, request):
        serializer = MyUserSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data, status=HTTPStatus.OK)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk):
        user = self.request.user
        author = get_object_or_404(User, id=pk)
        if self.request.method == 'POST':
            serializer = SubscriptionSerializer(
                author,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=user, author=author)
            return Response(serializer.data, status=HTTPStatus.CREATED)
        if self.request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscription,
                user=user,
                author=author
            )
            subscription.delete()
            return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscriber__user=request.user)
        pag_qs = self.paginate_queryset(queryset)
        subscriptions = SubscriptionSerializer(
            pag_qs, many=True, context={'request': request}
        )
        return self.get_paginated_response(subscriptions.data)
