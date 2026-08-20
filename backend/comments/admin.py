from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "content", "post", "created_at")
    search_fields = ("content", "author__username", "post__title")
    list_filter = ("created_at",)
