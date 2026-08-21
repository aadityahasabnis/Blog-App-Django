from django.contrib import admin

from .models import Follow, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "updated_at")
	search_fields = ("user__username", "user__email", "bio")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
	list_display = ("follower", "following", "created_at")
	search_fields = ("follower__username", "following__username")
