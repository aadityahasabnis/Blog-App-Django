from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import PostForm, SignUpForm
from .models import Post


def allPostData(post):
    return {
        "id": str(post.id),
        "title": post.title,
        "content": post.content,
        "author": {
            "id": post.author.id,
            "name": post.author.get_full_name() or post.author.username,
            "email": post.author.email,
        },
        "category": post.category,
        "is_published": post.is_published,
        "views": post.views,
        "created_at": post.created_at,
    }

def json_object(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, JsonResponse({"error": "Request body must contain valid JSON"}, status=400)
    if not isinstance(data, dict):
        return None, JsonResponse({"error": "Request body must be a JSON object"}, status=400)
    return data, None


def can_manage_post(user, post):
    return (
        user.is_staff
        or user.is_superuser
        or post.author_id == user.id
    )

def post_list(request):
    search_query = request.GET.get("q", "").strip()
    posts = Post.objects.filter(is_published=True).select_related("author")
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query)
            | Q(content__icontains=search_query)
            | Q(category__icontains=search_query)
            | Q(author__username__icontains=search_query)
        )

    posts = posts.order_by("-created_at").order_by("-views")
    page_obj = Paginator(posts, 6).get_page(request.GET.get("page"))
    return render(
        request,
        "blog/post_list.html",
        {"page_obj": page_obj, "search_query": search_query},
    )


@login_required
def my_posts(request):
    posts = Post.objects.filter(author=request.user).order_by("-created_at")
    return render(request, "blog/my_posts.html", {"posts": posts})

@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return render(request, "blog/post_created.html", {"post": post}, status=201)
    else:
        form = PostForm()

    return render(request, "blog/post_form.html", {"form": form})


@csrf_exempt
def post_create_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    data, error = json_object(request)
    if error:
        return error

    missing_fields = [field for field in ("title", "content") if not data.get(field)]
    if missing_fields:
        return JsonResponse(
            {"error": "Missing required fields", "fields": missing_fields},
            status=400,
        )

    post = Post.objects.create(
        title=data["title"],
        content=data["content"],
        author=request.user,
        category=data.get("category"),
        is_published=data.get("is_published", False),
    )

    return JsonResponse(allPostData(post), status=201)


@csrf_exempt
def post_detail(request, id):
    try:
        post = Post.objects.select_related("author").get(id=id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)

    if request.method == "GET":
        if not post.is_published:
            return JsonResponse({'error': 'Post not found'}, status=404)
        Post.objects.filter(id=post.id).update(views=F("views") + 1)
        post.refresh_from_db()
        if request.headers.get("Accept") == "application/json":
            return JsonResponse(allPostData(post))
        return render(request, "blog/post_detail.html", {"post": post})

    if request.method == "DELETE":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        if not can_manage_post(request.user, post):
            return JsonResponse({"error": "Permission denied"}, status=403)
        post.delete()
        return HttpResponse(status=204)

    if request.method not in ("PUT", "PATCH"):
        return JsonResponse(
            {"error": "Method not allowed", "allowed_methods": ["GET", "PUT", "PATCH", "DELETE"]},
            status=405,
        )

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)
    if not can_manage_post(request.user, post):
        return JsonResponse({"error": "Permission denied"}, status=403)

    data, error = json_object(request)
    if error:
        return error

    editable_fields = {"title", "content", "category", "is_published"}
    unknown_fields = sorted(set(data) - editable_fields)
    if unknown_fields:
        return JsonResponse(
            {"error": "Unknown fields", "fields": unknown_fields},
            status=400,
        )

    if request.method == "PUT":
        missing_fields = [field for field in ("title", "content") if not data.get(field)]
        if missing_fields:
            return JsonResponse(
                {"error": "PUT requires all fields", "fields": missing_fields},
                status=400,
            )

    update_data = {
        field: data[field]
        for field in ("title", "content", "category", "is_published")
        if field in data
    }
    if request.method == "PUT":
        post.title = update_data["title"]
        post.content = update_data["content"]
        post.category = update_data.get("category")
        post.is_published = update_data.get("is_published", False)
        post.save()
    else:
        Post.objects.filter(id=id).update(**update_data)
        post.refresh_from_db()

    return JsonResponse(allPostData(post), status=200)


def post_edit(request, id):
    if not request.user.is_authenticated:
        return redirect(f"/blogs/login/?next=/blogs/{id}/edit/")
    post = get_object_or_404(Post.objects.select_related("author"), id=id)
    if not can_manage_post(request.user, post):
        return HttpResponse("Permission denied", status=403)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect("post_view", id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, "blog/post_form.html", {"form": form, "post": post})


def post_delete(request, id):
    if not request.user.is_authenticated:
        return redirect(f"/blogs/login/?next=/blogs/{id}/delete/")
    post = get_object_or_404(Post, id=id)
    if not can_manage_post(request.user, post):
        return HttpResponse("Permission denied", status=403)
    if request.method == "POST":
        post.delete()
        return redirect("post_list")
    return render(request, "blog/post_confirm_delete.html", {"post": post})


def home(request):
    return render(request, "blog/home.html")


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("post_list")

    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            user = form.save()
        login(request, user)
        return redirect("post_list")

    return render(
        request,
        "blog/auth_form.html",
        {"form": form, "title": "Create an account", "action": "Sign up"},
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("post_list")

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get("next") or "post_list")

    return render(
        request,
        "blog/auth_form.html",
        {"form": form, "title": "Log in", "action": "Log in"},
    )


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("home")

def inspect_request(request):
    # request.session["favorite_color"] = "blue"
    try:
        body = request.body.decode("utf-8")
    except Exception:
        body = ""

    data = {
        "method": request.method,
        "path": request.path,
        "full_path": request.get_full_path(),

        "query_params": dict(request.GET),

        "form_data": dict(request.POST),

        "headers": dict(request.headers),

        "cookies": request.COOKIES,

        "content_type": request.content_type,

        "content_length": request.headers.get("Content-Length"),

        "body": body,

        "files": list(request.FILES.keys()),
    }

    response = JsonResponse(data)
    # response["X-Custom-Header"] = "Custom Value"
    # response.set_cookie(
    #     "new_username",
    #     "Aadi"
    # )
    # response.delete_cookie("username")
    # response.delete_header("X-Custom-Header")
    return response

def counter_view(request, count):
    return HttpResponse(f"Counter: {count} Bananas")