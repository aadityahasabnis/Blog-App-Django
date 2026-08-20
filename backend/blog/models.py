from django.db import models
from django.conf import settings
import uuid
# Create your models here.


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )

    content = models.TextField()

    category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    is_published = models.BooleanField(default=False)

    views = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def word_count(self):
        return len(self.content.split())