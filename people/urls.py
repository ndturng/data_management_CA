from django.urls import path

from . import views

urlpatterns = [
    path("", views.people_list, name="people_list"),
    path("new/", views.person_create, name="person_create"),
    path("<int:pk>/edit/", views.person_update, name="person_update"),
    path("<int:pk>/delete/", views.person_delete, name="person_delete"),
]
