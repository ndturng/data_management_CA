from django.urls import path

from . import views

urlpatterns = [
    path("", views.officer_list, name="officer_list"),
    path("new/", views.officer_create, name="officer_create"),
    path("<int:pk>/edit/", views.officer_update, name="officer_update"),
    path("<int:pk>/delete/", views.officer_delete, name="officer_delete"),
]
