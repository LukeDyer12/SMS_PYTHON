from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from . import views
from .views import (
    teacher_dashboard,
    teacher_portal,
    student_portal,
    portal_redirect,
    parent_portal,
    create_parent,
    student_report_pdf,
    manage_students,
    delete_assignment,
)


urlpatterns = [

    # -----------------------------------------------------
    # HOME
    # -----------------------------------------------------
    path("", views.home, name="home"),


    # -----------------------------------------------------
    # STUDENTS
    # -----------------------------------------------------
    path("students/", views.student_list, name="student_list"),
    path("students/create/", views.create_student, name="create_student"),
    path("students/<int:pk>/edit/", views.edit_student, name="edit_student"),
    path("students/<int:pk>/delete/", views.delete_student, name="delete_student"),
    path("students/<int:pk>/", views.student_detail, name="student_detail"),

    # Attendance
    path("students/<int:pk>/attendance/history/", views.student_attendance_history, name="student_attendance_history"),
    path("students/<int:pk>/attendance/summary/", views.student_attendance_summary, name="student_attendance_summary"),

    # Photos
    path("students/<int:pk>/remove-photo/", views.remove_student_photo, name="remove_student_photo"),
    path("students/<int:pk>/upload-photo/", views.upload_student_photo, name="upload_student_photo"),

    # Reports (fixed duplicate)
    path("students/<int:student_id>/report/", student_report_pdf, name="student_report_pdf"),

    # Student Portal
    path("portal/student/", student_portal, name="student_portal"),


    # -----------------------------------------------------
    # TEACHERS
    # -----------------------------------------------------
    path("teachers/", views.teacher_list, name="teacher_list"),
    path("teachers/create/", views.create_teacher, name="create_teacher"),
    path("teachers/<int:pk>/edit/", views.edit_teacher, name="edit_teacher"),
    path("teachers/<int:pk>/delete/", views.delete_teacher, name="delete_teacher"),
    path("teachers/<int:pk>/", views.teacher_detail, name="teacher_detail"),

    # Teacher Portal (cleaned)
    path("portal/teacher/", teacher_portal, name="teacher_portal"),
    path("portal/teacher/dashboard/", teacher_dashboard, name="teacher_dashboard"),


    # -----------------------------------------------------
    # CLASSROOMS
    # -----------------------------------------------------
    path("classrooms/", views.classroom_list, name="classroom_list"),
    path("classrooms/create/", views.create_classroom, name="create_classroom"),
    path("classrooms/<int:pk>/", views.classroom_detail, name="classroom_detail"),
    path("classrooms/<int:pk>/edit/", views.edit_classroom, name="edit_classroom"),
    path("classrooms/<int:pk>/delete/", views.delete_classroom, name="delete_classroom"),

    # Classroom student management
    path("classrooms/<int:pk>/add-student/", views.add_student_to_classroom, name="add_student_to_classroom"),
    path("classrooms/<int:classroom_pk>/remove-student/<int:student_pk>/", views.remove_student_from_classroom, name="remove_student_from_classroom"),
    path("classrooms/<int:classroom_id>/students/", views.manage_students, name="manage_students"),


    # Attendance
    path("classrooms/<int:pk>/attendance/", views.take_attendance, name="take_attendance"),
    path("classrooms/<int:pk>/attendance/history/", views.classroom_attendance_history, name="classroom_attendance_history"),
    path("classrooms/<int:pk>/attendance/summary/", views.classroom_attendance_summary, name="classroom_attendance_summary"),

    # Assignments
    path("classrooms/<int:classroom_id>/assignments/", views.assignment_list, name="assignment_list"),
    path("classrooms/<int:classroom_id>/assignments/add/", views.add_assignment, name="add_assignment"),
    path("assignments/<int:pk>/delete/", views.delete_assignment, name="delete_assignment"),



    # -----------------------------------------------------
    # ASSIGNMENTS (grading)
    # -----------------------------------------------------
    path("assignments/<int:assignment_id>/grades/", views.enter_grades, name="enter_grades"),
    path("assignments/<int:pk>/", views.assignment_detail, name="assignment_detail"),
    path("assignments/<int:assignment_id>/grade/<int:student_id>/", views.enter_grade, name="enter_grade"),
    path("assignments/<int:assignment_id>/missing/<int:student_id>/", views.mark_missing, name="mark_missing"),
    path("assignments/<int:assignment_id>/update/<int:student_id>/", views.update_grade, name="update_grade"),


    # -----------------------------------------------------
    # DASHBOARD
    # -----------------------------------------------------
    path("dashboard/", views.dashboard, name="dashboard"),


    # -----------------------------------------------------
    # LOGIN / LOGOUT
    # -----------------------------------------------------
    path("login/", auth_views.LoginView.as_view(template_name="core/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),


    # -----------------------------------------------------
    # PORTAL REDIRECT (role-based)
    # -----------------------------------------------------
    path("portal/", portal_redirect, name="portal_redirect"),


    # -----------------------------------------------------
    # PARENTS
    # -----------------------------------------------------
    path("portal/parent/", parent_portal, name="parent_portal"),
    path("parents/create/", create_parent, name="create_parent"),
    path("parent/", views.parent_dashboard, name="parent_dashboard"),
    #temp
    path("backfill-grades/", views.backfill_grades),

]


# ---------------------------------------------------------
# MEDIA FILES (development only)
# ---------------------------------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
