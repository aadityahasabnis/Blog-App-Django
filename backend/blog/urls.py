from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('inspect/', views.inspect_request),
    path('counter/<int:count>', views.counter_view)
]