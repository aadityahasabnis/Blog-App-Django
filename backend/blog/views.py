from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Author, Post

# Create your views here.
def post_list(request):
    posts = Post.objects.filter(is_published=True).exclude(views=0).order_by('-views').select_related('author').all()
    return JsonResponse({
        'posts': [
            {
                'id': str(post.id),
                'title': post.title,
                'content': post.content,
                'author': {
                        "id": post.author.id,
                        "name": post.author.name,
                        "email": post.author.email,
                    },
                'category': post.category,
                'is_published': post.is_published,
                "views": post.views,
                "created_at": post.created_at,
            }
            for post in posts
        ]
    })


@csrf_exempt
def post_create(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Request body must contain valid JSON"}, status=400)

    if not isinstance(data, dict):
        return JsonResponse({"error": "Request body must be a JSON object"}, status=400)

    missing_fields = [field for field in ("title", "content", "author_id") if not data.get(field)]
    if missing_fields:
        return JsonResponse(
            {"error": "Missing required fields", "fields": missing_fields},
            status=400,
        )

    try:
        author = Author.objects.get(id=data["author_id"])
    except (Author.DoesNotExist, ValueError, TypeError):
        return JsonResponse({"error": "Author not found"}, status=404)

    post = Post.objects.create(
        title=data["title"],
        content=data["content"],
        author=author,
        category=data.get("category"),
        is_published=data.get("is_published", False),
    )

    return JsonResponse(
        {
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
        },
        status=201,
    )


def post_data(post):
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


@csrf_exempt
def post_detail(request, id):
    try:
        post = Post.objects.select_related("author").get(id=id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)

    if request.method == "GET":
        if not post.is_published:
            return JsonResponse({'error': 'Post not found'}, status=404)
        return JsonResponse(post_data(post))

    if request.method == "DELETE":
        post.delete()
        return HttpResponse(status=204)

    if request.method not in ("PUT", "PATCH"):
        return JsonResponse(
            {"error": "Method not allowed", "allowed_methods": ["GET", "PUT", "PATCH", "DELETE"]},
            status=405,
        )

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Request body must contain valid JSON"}, status=400)

    if not isinstance(data, dict):
        return JsonResponse({"error": "Request body must be a JSON object"}, status=400)

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
        try:
            author = Author.objects.get(id=data["author_id"])
        except (Author.DoesNotExist, ValueError, TypeError):
            return JsonResponse({"error": "Author not found"}, status=404)
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

    return JsonResponse(post_data(post), status=200)


def home(request):
    data = {
        "method": request.method,
        "path": request.path,
        "full_path": request.get_full_path(),
        "query": dict(request.GET),
        "search": request.GET.getlist("search"),
        "scheme": request.scheme,
        "content_type": request.content_type,
        "headers": dict(request.headers),
        "meta_keys": list(request.META.keys()),
        "REQUEST_METHOD": request.META["REQUEST_METHOD"],
        "REMOTE_ADDR": request.META["REMOTE_ADDR"],
        "SERVER_NAME": request.META["SERVER_NAME"],
        "SERVER_PORT": request.META["SERVER_PORT"],
        "QUERY_STRING": request.META["QUERY_STRING"],
        "HTTP_USER_AGENT": request.META.get("HTTP_USER_AGENT"),
        "HTTP_ACCEPT": request.META.get("HTTP_ACCEPT"),
    }

    meta = {
        key: str(value)
        for key, value in request.META.items()
    }
    # return JsonResponse({
    #     "meta": meta
    # })
    return JsonResponse(data)

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