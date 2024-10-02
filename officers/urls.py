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
    # Quá trình công tác
    path(
        "<int:pk>/work-process",
        views.WorkProcessListView.as_view(),
        name="url_work_process",
    ),
    path(
        "<int:pk>/work-process/create",
        views.WorkProcessCreateView.as_view(),
        name="url_work_process_create",
    ),
    path(
        "<int:pk>/work-process/update/<int:work_process_pk>",
        views.WorkProcessUpdateView.as_view(),
        name="url_work_process_update",
    ),
    path(
        "<int:pk>/work-process/delete/<int:work_process_pk>",
        views.WorkProcessDeleteView.as_view(),
        name="url_work_process_delete",
    ),
    ############################################################
    # Quá trình lương
    path(
        "<int:pk>/salary-process",
        views.SalaryProcessListView.as_view(),
        name="url_salary_process",
    ),
    path(
        "<int:pk>/salary-process/create",
        views.SalaryProcessCreateView.as_view(),
        name="url_salary_process_create",
    ),
    path(
        "<int:pk>/salary-process/update/<int:salary_process_pk>",
        views.SalaryProcessUpdateView.as_view(),
        name="url_salary_process_update",
    ),
    path(
        "<int:pk>/salary-process/delete/<int:salary_process_pk>",
        views.SalaryProcessDeleteView.as_view(),
        name="url_salary_process_delete",
    ),
    ############################################################
    # Khen thưởng
    path(
        "<int:pk>/laudatory", 
        views.LaudatoryListView.as_view(),
        name="url_laudatory"
    ),
    path(
        "<int:pk>/laudatory/create",
        views.LaudatoryCreateView.as_view(),
        name="url_laudatory_create"
    ),
    path(
        "<int:pk>/laudatory/update/<int:laudatory_pk>",
        views.LaudatoryUpdateView.as_view(),
        name="url_laudatory_update"
    ),
    path(
        "<int:pk>/laudatory/delete/<int:laudatory_pk>",
        views.LaudatoryDeleteView.as_view(),
        name="url_laudatory_delete"
    ),
    ############################################################
    # Kỷ luật
    path(
        "<int:pk>/discipline",
        views.DisciplineListView.as_view(),
        name="url_discipline",
    ),
    path(
        "<int:pk>/discipline/create",
        views.DisciplineCreateView.as_view(),
        name="url_discipline_create",
    ),
    path(
        "<int:pk>/discipline/update/<int:discipline_pk>",
        views.DisciplineUpdateView.as_view(),
        name="url_discipline_update",
    ),
    path(
        "<int:pk>/discipline/delete/<int:discipline_pk>",
        views.DisciplineDeleteView.as_view(),
        name="url_discipline_delete",
    ),
    ############################################################
    # Thân nhân
    path(
        "<int:pk>/relative",
        views.RelativeListView.as_view(),
        name="url_relative",
    ),
    path(
        "<int:pk>/relative/create",
        views.RelativeCreateView.as_view(),
        name="url_relative_create",
    ),
    path(
        "<int:pk>/relative/update/<int:relative_pk>",
        views.RelativeUpdateView.as_view(),
        name="url_relative_update",
    ),
    path(
        "<int:pk>/relative/delete/<int:relative_pk>",
        views.RelativeDeleteView.as_view(),
        name="url_relative_delete",
    ),
    ############################################################
    path("<int:pk>/abroad", views.officer_abroad, name="officer_abroad"),
    path(
        "<int:pk>/army-join-history",
        views.officer_army_join_history,
        name="officer_army_join_history",
    ),
    path("<int:pk>/health", views.officer_health, name="officer_health"),
]
