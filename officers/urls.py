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
    path("<int:pk>/titles/", views.officer_title, name="officer_title_view"),
    path(
        "<int:pk>/titles/manage/",
        views.officer_title_manage,
        name="officer_title_add",
    ),
    path(
        "<int:pk>/titles/manage/<int:title_id>/",
        views.officer_title_manage,
        name="officer_title_edit",
    ),
    path(
        "officer/<int:pk>/titles/<int:title_id>/delete/",
        views.delete_title,
        name="delete_title",
    ),
    path(
        "<int:pk>/position-plan",
        views.officer_position_plan,
        name="officer_position_plan",
    ),
    path(
        "<int:pk>/learning-path",
        views.officer_learning_path,
        name="officer_learning_path",
    ),
    path(
        "<int:pk>/work-process",
        views.officer_work_process,
        name="officer_work_process",
    ),
    path(
        "<int:pk>/salary-process",
        views.officer_salary_process,
        name="officer_salary_process",
    ),
    path(
        "<int:pk>/laudatory", views.officer_laudatory, name="officer_laudatory"
    ),
    path(
        "<int:pk>/discipline",
        views.officer_discipline,
        name="officer_discipline",
    ),
    path("<int:pk>/relative", views.officer_relative, name="officer_relative"),
    path("<int:pk>/abroad", views.officer_abroad, name="officer_abroad"),
    path(
        "<int:pk>/army-join-history",
        views.officer_army_join_history,
        name="officer_army_join_history",
    ),
    path("<int:pk>/health", views.officer_health, name="officer_health"),
]
