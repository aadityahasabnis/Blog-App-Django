from .models import Author, Post
from django.contrib import admin
import site

# Register your models here.
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
    )

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
        "author__name",
    )

    ordering = (
        "-created_at",
    )