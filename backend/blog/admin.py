from django.contrib import admin

from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "author",
        "category",
        "is_published",
        "views",
        "comment_count",
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

    def get_queryset(self, request):
        return super().get_queryset(request).with_comment_count()

    @admin.display(description="Comments", ordering="comment_count")
    def comment_count(self, obj):
        return obj.comment_count