from django.conf import settings
from django.db import models
from django.db.models import F, Q


class Profile(models.Model):
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="profile",
	)
	bio = models.TextField(blank=True)
	avatar = models.FileField(upload_to="avatars/", blank=True, null=True)
	website_url = models.URLField(blank=True)
	twitter_url = models.URLField(blank=True)
	github_url = models.URLField(blank=True)
	linkedin_url = models.URLField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Profile({self.user.username})"

	def follower_count(self):
		return self.user.followers.count()

	def following_count(self):
		return self.user.following.count()


class Follow(models.Model):
	follower = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="following",
	)
	following = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="followers",
	)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]
		constraints = [
			models.UniqueConstraint(
				fields=["follower", "following"],
				name="unique_follow_relationship",
			),
			models.CheckConstraint(
				condition=~Q(follower=F("following")),
				name="prevent_self_follow",
			),
		]

	def __str__(self):
		return f"{self.follower.username} -> {self.following.username}"
