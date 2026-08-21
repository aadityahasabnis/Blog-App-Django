from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from blog.models import Post

from .forms import ProfileForm
from .models import Follow, Profile

User = get_user_model()


def can_edit_profile(user, target_user):
	return user.is_authenticated and user.id == target_user.id


def can_follow_user(user, target_user):
	return user.is_authenticated and user.id != target_user.id


def author_page(request, username):
	author = get_object_or_404(User, username=username)
	profile, _ = Profile.objects.get_or_create(user=author)
	posts = (
		Post.objects.filter(author=author, is_published=True)
		.with_comment_count()
		.order_by("-created_at")
	)
	is_following = False
	if request.user.is_authenticated and request.user.id != author.id:
		is_following = Follow.objects.filter(
			follower=request.user,
			following=author,
		).exists()

	context = {
		"author": author,
		"profile": profile,
		"posts": posts,
		"is_following": is_following,
		"follower_count": author.followers.count(),
		"following_count": author.following.count(),
	}
	return render(request, "profiles/author_page.html", context)


@login_required
def profile_edit(request):
	profile, _ = Profile.objects.get_or_create(user=request.user)

	if request.method == "POST":
		form = ProfileForm(request.POST, request.FILES, instance=profile)
		if form.is_valid():
			form.save()
			return redirect("author_page", username=request.user.username)
	else:
		form = ProfileForm(instance=profile)

	return render(request, "profiles/edit_profile.html", {"form": form, "profile": profile})


@login_required
def follow_toggle(request, username):
	if request.method != "POST":
		return redirect("author_page", username=username)

	target_user = get_object_or_404(User, username=username)
	if not can_follow_user(request.user, target_user):
		return HttpResponse("Permission denied", status=403)

	follow, created = Follow.objects.get_or_create(
		follower=request.user,
		following=target_user,
	)
	if not created:
		follow.delete()

	return redirect("author_page", username=target_user.username)
