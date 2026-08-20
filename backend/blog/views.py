from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import PostForm
from .models import Author, Post


def allPostData(post):
    return {
        "id": str(post.id),
        "title": post.title,
        "content": post.content,
        "author": {
            "id": post.author.id,
            "name": post.author.name,
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


def isAndGetAuthor(author_id):
    try:
        return Author.objects.get(id=author_id), None
    except (Author.DoesNotExist, ValueError, TypeError):
        return None, JsonResponse({"error": "Author not found"}, status=404)

def post_list(request):
    search_query = request.GET.get("q", "").strip()
    posts = Post.objects.filter(is_published=True).select_related("author")
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query)
            | Q(content__icontains=search_query)
            | Q(category__icontains=search_query)
            | Q(author__name__icontains=search_query)
        )

    posts = posts.order_by("-created_at").order_by("-views")
    page_obj = Paginator(posts, 6).get_page(request.GET.get("page"))
    return render(
        request,
        "blog/post_list.html",
        {"page_obj": page_obj, "search_query": search_query},
    )

def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save()
            return render(request, "blog/post_created.html", {"post": post}, status=201)
    else:
        form = PostForm()

    return render(request, "blog/post_form.html", {"form": form})


@csrf_exempt
def post_create_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    data, error = json_object(request)
    if error:
        return error

    missing_fields = [field for field in ("title", "content", "author_id") if not data.get(field)]
    if missing_fields:
        return JsonResponse(
            {"error": "Missing required fields", "fields": missing_fields},
            status=400,
        )

    author, error = isAndGetAuthor(data["author_id"])
    if error:
        return error

    post = Post.objects.create(
        title=data["title"],
        content=data["content"],
        author=author,
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
        post.delete()
        return HttpResponse(status=204)

    if request.method not in ("PUT", "PATCH"):
        return JsonResponse(
            {"error": "Method not allowed", "allowed_methods": ["GET", "PUT", "PATCH", "DELETE"]},
            status=405,
        )

    data, error = json_object(request)
    if error:
        return error

    editable_fields = {"title", "content", "author_id", "category", "is_published"}
    unknown_fields = sorted(set(data) - editable_fields)
    if unknown_fields:
        return JsonResponse(
            {"error": "Unknown fields", "fields": unknown_fields},
            status=400,
        )

    if request.method == "PUT":
        missing_fields = [field for field in ("title", "content", "author_id") if not data.get(field)]
        if missing_fields:
            return JsonResponse(
                {"error": "PUT requires all fields", "fields": missing_fields},
                status=400,
            )

    if "author_id" in data:
        author, error = isAndGetAuthor(data["author_id"])
        if error:
            return error
    else:
        author = post.author

    update_data = {
        field: data[field]
        for field in ("title", "content", "category", "is_published")
        if field in data
    }
    update_data["author"] = author

    if request.method == "PUT":
        post.title = update_data["title"]
        post.content = update_data["content"]
        post.author = update_data["author"]
        post.category = update_data.get("category")
        post.is_published = update_data.get("is_published", False)
        post.save()
    else:
        Post.objects.filter(id=id).update(**update_data)
        post.refresh_from_db()
        post.author = Author.objects.get(id=post.author_id)

    return JsonResponse(allPostData(post), status=200)


def post_edit(request, id):
    post = get_object_or_404(Post.objects.select_related("author"), id=id)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect("post_view", id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, "blog/post_form.html", {"form": form, "post": post})


def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    if request.method == "POST":
        post.delete()
        return redirect("post_list")
    return render(request, "blog/post_confirm_delete.html", {"post": post})


def home(request):
    return render(request, "blog/home.html")

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