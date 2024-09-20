from django.urls import path

from . import views

urlpatterns = [
    path("", views.officer_list, name="officer_list"),
    path("new/", views.officer_create, name="officer_create"),
    path("upload-excel/", views.excel_upload, name="excel_upload"),
    path("<int:pk>/", views.officer_detail, name="officer_detail"),
    path("<int:pk>/edit/", views.officer_update, name="officer_update"),
    path("<int:pk>/delete/", views.officer_delete, name="officer_delete"),
    path("delete-all/", views.delete_all_officers, name="delete_all_officers"),
    path("<int:pk>/title", views.officer_title, name="officer_title"),
    path("<int:pk>/position-plan", views.officer_position_plan, name="officer_position_plan"),
]
