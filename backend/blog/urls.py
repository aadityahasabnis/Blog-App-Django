from django.urls import path
from . import views

urlpatterns = [
    path("", views.post_list, name="post_list"),
    path("create/", views.post_create, name="post_create"),
    path("api/create/", views.post_create_api, name="post_create_api"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("mine/", views.my_posts, name="my_posts"),
    path('<uuid:id>/edit/', views.post_edit, name='post_edit'),
    path('<uuid:id>/delete/', views.post_delete, name='post_delete'),
    path('<uuid:id>/', views.post_detail, name='post_view'),
    path('inspect/', views.inspect_request),
    path('counter/<int:count>', views.counter_view)
]