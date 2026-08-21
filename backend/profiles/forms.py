from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "bio",
            "avatar",
            "website_url",
            "twitter_url",
            "github_url",
            "linkedin_url",
        ]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 6}),
            "avatar": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }
