from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from blog.models import Post
from .forms import CommentForm
from .models import Comment

COMMENTS_PER_PAGE = 5


def comments_for_post(post):
    return post.comments.select_related("author").order_by("-created_at")


def comment_page(post, page_number):
    paginator = Paginator(comments_for_post(post), COMMENTS_PER_PAGE)
    try:
        return paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        return None


def can_manage_comment(user, comment):
    return user.is_authenticated and comment.author_id == user.id


@login_required
def create_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, is_published=True)
    if request.method != "POST":
        return redirect("post_view", id=post.id)

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect("post_view", id=post.id)

    page_obj = comment_page(post, 1)
    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
            "comment_form": form,
            "comments_page": page_obj,
            "comment_count": comments_for_post(post).count(),
        },
        status=400,
    )


def load_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id, is_published=True)
    page_obj = comment_page(post, request.GET.get("page", 2))
    if page_obj is None:
        return HttpResponse("", status=404)
    return render(
        request,
        "comments/comment_items.html",
        {"comments_page": page_obj, "post": post},
    )


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment.objects.select_related("post", "author"), id=comment_id)
    if not can_manage_comment(request.user, comment):
        return HttpResponse("Permission denied", status=403)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect("post_view", id=comment.post_id)
    else:
        form = CommentForm(instance=comment)

    return render(request, "comments/edit_comment.html", {"form": form, "comment": comment})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment.objects.select_related("post", "author"), id=comment_id)
    if not can_manage_comment(request.user, comment):
        return HttpResponse("Permission denied", status=403)

    if request.method == "POST":
        post_id = comment.post_id
        comment.delete()
        return redirect("post_view", id=post_id)

    return render(request, "comments/delete_comment.html", {"comment": comment})


@login_required
def my_comments(request):
    comments = (
        Comment.objects.filter(author=request.user)
        .select_related("post")
        .order_by("-created_at")
    )
    return render(request, "comments/my_comments.html", {"comments": comments})
