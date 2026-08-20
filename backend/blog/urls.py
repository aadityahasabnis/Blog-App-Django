from django.urls import path
from . import views

urlpatterns = [
    path("", views.post_list, name="post_list"),
    path("create/", views.post_create, name="post_create"),
    path('<uuid:id>', views.post_detail, name='post_view'),
    path('inspect/', views.inspect_request),
    path('counter/<int:count>', views.counter_view)
]