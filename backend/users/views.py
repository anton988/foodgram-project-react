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
        if user == author:
            return Response(
                {'error': 'Вы не можете подписаться на самого себя'},
                status=HTTPStatus.BAD_REQUEST
            )
        if self.request.method == 'POST':
            existing_subscription = Subscription.objects.filter(
                subscriber=user, author=author
            ).exists()
            if existing_subscription:
                return Response(
                    {'error': 'Вы уже подписаны на этого автора'},
                    status=HTTPStatus.BAD_REQUEST
                )
            subscription = Subscription.objects.create(
                author=author,
                subscriber=user,
            )
            subscription.save()
            serializator = SubscriptionSerializer(
                subscription, context={'request': request}
            )
            return Response(serializator.data, HTTPStatus.CREATED)
        if self.request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                author=author,
                subscriber=user
            ).first()
            if subscription:
                subscription.delete()
                return Response('Вы отписались', status=HTTPStatus.NO_CONTENT)
            return Response(
                'Подписка не найдена',
                status=HTTPStatus.BAD_REQUEST
            )

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        subscribers = Subscription.objects.filter(subscriber=request.user)
        pages = self.paginate_queryset(subscribers)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
