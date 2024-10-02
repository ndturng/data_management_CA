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
    ############################################################
    # Chức danh
    path(
        "<int:pk>/titles/",
        views.TitleListView.as_view(),
        name="url_title_view",
    ),
    path(
        "<int:pk>/titles/create/",
        views.TitleCreateView.as_view(),
        name="url_title_create",
    ),
    path(
        "<int:pk>/titles/update/<int:title_pk>/",
        views.TitleUpdateView.as_view(),
        name="url_title_update",
    ),
    path(
        "<int:pk>/titles/delete/<int:title_pk>/",
        views.TitleDeleteView.as_view(),
        name="url_title_delete",
    ),
    ############################################################
    # Quy hoạch
    path(
        "<int:pk>/position_plans/",
        views.PositionPlanListView.as_view(),
        name="url_position_plan",
    ),
    path(
        "<int:pk>/position_plans/create/",
        views.PositionPlanCreateView.as_view(),
        name="url_position_plan_create",
    ),
    path(
        "<int:pk>/position_plans/update/<int:position_plan_pk>/",
        views.PositionPlanUpdateView.as_view(),
        name="url_position_plan_update",
    ),
    path(
        "<int:pk>/position_plans/delete/<int:position_plan_pk>/",
        views.PositionPlanDeleteView.as_view(),
        name="url_position_plan_delete",
    ),
    ############################################################
    # Đào tạo
    path(
        "<int:pk>/learning-path",
        views.LearningPathListView.as_view(),
        name="url_learning_path",
    ),
    path(
        "<int:pk>/learning-path/create",
        views.LearningPathCreateView.as_view(),
        name="url_learning_path_create",
    ),
    path(
        "<int:pk>/learning-path/update/<int:learning_path_pk>",
        views.LearningPathUpdateView.as_view(),
        name="url_learning_path_update",
    ),
    path(
        "<int:pk>/learning-path/delete/<int:learning_path_pk>",
        views.LearningPathDeleteView.as_view(),
        name="url_learning_path_delete",
    ),
    ############################################################
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
