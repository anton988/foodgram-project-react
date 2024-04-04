from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

app_name = 'users'

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    url('', include('djoser.urls')),
    url('auth/', include('djoser.urls.authtoken'))
]
