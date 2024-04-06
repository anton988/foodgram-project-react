from django.contrib import admin
from .models import User, Subscription


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_per_page = 20


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'subscriber')
    search_fields = ('author__username',)
    list_filter = ('author__username', 'subscriber__username')
    raw_id_fields = ('author', 'subscriber')
    list_per_page = 20
