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
from .serializers import (
    MyUserSerializer, SubscriptionSerializer, SubscriptionCreateSerializer
)


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
            existing_subscription = Subscription.objects.filter(
                subscriber=user, author=author
            ).exists()
            if existing_subscription:
                return Response(
                    {'error': 'Вы уже подписаны на этого автора'},
                    status=HTTPStatus.BAD_REQUEST
                )
            serializer = SubscriptionCreateSerializer(
                data={'author': author.pk, 'subscriber': user.pk},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=HTTPStatus.CREATED)
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
        subscribers = User.objects.filter(subscriber__author=request.user)
        pages = self.paginate_queryset(subscribers)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
