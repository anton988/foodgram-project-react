from djoser.views import UserViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    SAFE_METHODS, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from recipes.filters import RecipeTagFilter
from .models import User
from .permissions import IsAdmin, IsOwnerOrReadOnly
from .serializers import UserSerializer


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsOwnerOrReadOnly,)
