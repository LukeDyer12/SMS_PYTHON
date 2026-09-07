from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages

from .models import Parent, Student, Teacher, Classroom, Assignment


# ---------------------------------------------------------
# Custom AdminSite
# ---------------------------------------------------------
class SchoolAdminSite(admin.AdminSite):
    site_header = "School Management System"
    site_title = "School Admin"
    index_title = "Dashboard"
    site_url = None


admin_site = SchoolAdminSite(name="school_admin")


# ---------------------------------------------------------
# Helper: Reset password logic
# ---------------------------------------------------------
def reset_user_password(user_obj):
    new_password = "password123"
    user_obj.set_password(new_password)
    user_obj.save()
    return new_password


# ---------------------------------------------------------
# Parent Admin
# ---------------------------------------------------------
class ParentAdmin(admin.ModelAdmin):
    list_display = ("get_first_name", "get_last_name", "get_email", "reset_password_button")

    def get_first_name(self, obj):
        return obj.user.first_name if obj.user else "(no user)"
    get_first_name.short_description = "First Name"

    def get_last_name(self, obj):
        return obj.user.last_name if obj.user else "(no user)"
    get_last_name.short_description = "Last Name"

    def get_email(self, obj):
        return obj.user.email if obj.user else "(no user)"
    get_email.short_description = "Email"

    def reset_password_button(self, obj):
        if not obj.user:
            return "No user"
        return mark_safe(
            f'<a class="button" href="parent/{obj.id}/reset_password/">Reset Password</a>'
        )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "parent/<int:parent_id>/reset_password/",
                self.admin_site.admin_view(self.reset_password_view),
                name="parent_reset_password",
            ),
        ]
        return custom + urls

    def reset_password_view(self, request, parent_id):
        parent = Parent.objects.get(id=parent_id)
        if not parent.user:
            messages.error(request, "This parent has no linked user account.")
            return redirect(f"/admin/core/parent/{parent_id}/change/")

        new_pw = reset_user_password(parent.user)
        messages.success(request, f"Password reset to: {new_pw}")
        return redirect(f"/admin/core/parent/{parent_id}/change/")


# ---------------------------------------------------------
# Student Admin
# ---------------------------------------------------------
class StudentAdmin(admin.ModelAdmin):
    list_display = ("get_first_name", "get_last_name", "classroom", "reset_password_button")

    def get_first_name(self, obj):
        return obj.user.first_name if obj.user else obj.first_name
    get_first_name.short_description = "First Name"

    def get_last_name(self, obj):
        return obj.user.last_name if obj.user else obj.last_name
    get_last_name.short_description = "Last Name"

    def reset_password_button(self, obj):
        if not obj.user:
            return "No user"
        return mark_safe(
            f'<a class="button" href="student/{obj.id}/reset_password/">Reset Password</a>'
        )
    reset_password_button.short_description = "Reset Password"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "student/<int:student_id>/reset_password/",
                self.admin_site.admin_view(self.reset_password_view),
                name="student_reset_password",
            ),
        ]
        return custom + urls

    def reset_password_view(self, request, student_id):
        student = Student.objects.get(id=student_id)
        if not student.user:
            messages.error(request, "This student has no linked user account.")
            return redirect(f"/admin/core/student/{student_id}/change/")

        new_pw = reset_user_password(student.user)
        messages.success(request, f"Password reset to: {new_pw}")
        return redirect(f"/admin/core/student/{student_id}/change/")


# ---------------------------------------------------------
# Teacher Admin
# ---------------------------------------------------------
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("get_first_name", "get_last_name", "get_email", "reset_password_button")

    def get_first_name(self, obj):
        return obj.user.first_name if obj.user else "(no user)"
    get_first_name.short_description = "First Name"

    def get_last_name(self, obj):
        return obj.user.last_name if obj.user else "(no user)"
    get_last_name.short_description = "Last Name"

    def get_email(self, obj):
        return obj.user.email if obj.user else "(no user)"
    get_email.short_description = "Email"

    def reset_password_button(self, obj):
        if not obj.user:
            return "No user"
        return mark_safe(
            f'<a class="button" href="teacher/{obj.id}/reset_password/">Reset Password</a>'
        )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "teacher/<int:teacher_id>/reset_password/",
                self.admin_site.admin_view(self.reset_password_view),
                name="teacher_reset_password",
            ),
        ]
        return custom + urls

    def reset_password_view(self, request, teacher_id):
        teacher = Teacher.objects.get(id=teacher_id)
        if not teacher.user:
            messages.error(request, "This teacher has no linked user account.")
            return redirect(f"/admin/core/teacher/{teacher_id}/change/")

        new_pw = reset_user_password(teacher.user)
        messages.success(request, f"Password reset to: {new_pw}")
        return redirect(f"/admin/core/teacher/{teacher_id}/change/")


# ---------------------------------------------------------
# Register models
# ---------------------------------------------------------
admin_site.register(Parent, ParentAdmin)
admin_site.register(Student, StudentAdmin)
admin_site.register(Teacher, TeacherAdmin)
admin_site.register(Classroom)
admin_site.register(Assignment)
