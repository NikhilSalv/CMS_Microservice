from django.contrib import admin
from .models import Profile, Friendship

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'avatar_url')
    search_fields = ('user__username', 'display_name')

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('requester', 'addressee', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('requester__username', 'addressee__username')
