from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json

# Create your views here.

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