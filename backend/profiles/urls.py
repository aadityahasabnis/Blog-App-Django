from django.urls import path

from . import views

urlpatterns = [
    path("authors/<str:username>/", views.author_page, name="author_page"),
    path("authors/<str:username>/follow/", views.follow_toggle, name="follow_toggle"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
]
