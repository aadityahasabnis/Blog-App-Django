from django.urls import path
from . import views

urlpatterns = [
    path("comments/mine/", views.my_comments, name="my_comments"),
    path("comments/<int:comment_id>/edit/", views.edit_comment, name="edit_comment"),
    path("comments/<int:comment_id>/delete/", views.delete_comment, name="delete_comment"),
    path("<uuid:post_id>/comments/", views.create_comment, name="create_comment"),
    path("<uuid:post_id>/comments/load/", views.load_comments, name="load_comments"),
]
