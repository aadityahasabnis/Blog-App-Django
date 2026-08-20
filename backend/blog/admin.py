from .models import Post
from django.contrib import admin

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "author",
        "category",
        "is_published",
        "views",
        "created_at",
    )

    list_filter = (
        "is_published",
        "category",
        "created_at",
    )

    search_fields = (
        "title",
        "content",
        "author__username",
    )

    ordering = (
        "-created_at",
    )