from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title",
            "author",
            "content",
            "category",
            "is_published",
        ]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 8}),
        }
