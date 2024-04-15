from http import HTTPStatus
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from foodgram.pagination import CustomPagination
from .models import User, Subscription
from .serializers import MyUserSerializer, SubscriptionSerializer


class MyUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = MyUserSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def me(self, request):
        me = self.get_serializer(request.user).data
        return Response(me, status=HTTPStatus.OK)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if self.request.method == 'POST':
            serializer = SubscriptionSerializer(
                author,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(subscriber=user, author=author)
            return Response(serializer.data, status=HTTPStatus.CREATED)
        if self.request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscription,
                author=author,
                subscriber=user
            )
            subscription.delete()
            return Response('Вы отписались', status=HTTPStatus.NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        subscribers = User.objects.filter(subscriber__author=request.user)
        pages = self.paginate_queryset(subscribers)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
