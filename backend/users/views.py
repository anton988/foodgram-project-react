from http import HTTPStatus
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from djoser.views import UserViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import User, Subscription
from .serializers import UserSerializer, SubscriptionSerializer


class UserViewSet(UserViewSet):
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    def dispatch(self, request, *args, **kwargs):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.dispatch = method_decorator(login_required)(super().dispatch)
        return super().dispatch(request, *args, **kwargs)

    def get_current_user(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=HTTPStatus.OK)

    def subscribe(self, request, pk):
        user = self.request.user
        author = get_object_or_404(User, pk=pk)
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

    def subscriptions(self, request):
        queryset = User.objects.filter(subscriber__user=request.user)
        pag_qs = self.paginate_queryset(queryset)
        subscriptions = SubscriptionSerializer(
            pag_qs, many=True, context={'request': request}
        )
        return self.get_paginated_response(subscriptions.data)
