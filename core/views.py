from datetime import date
import os
import base64
from io import BytesIO

from django import forms
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string

from xhtml2pdf import pisa
import qrcode

from .models import Student, Teacher, Classroom, Attendance, Assignment, Grade
from .forms import TeacherForm, StudentForm, ParentForm


# -------------------------
# HOME
# -------------------------
def home(request):
    return render(request, 'core/home.html')


# -------------------------
# DASHBOARD
# -------------------------
def dashboard(request):
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_classrooms = Classroom.objects.count()

    today = date.today()
    today_records = Attendance.objects.filter(date=today)

    present_today = today_records.filter(status='present').count()
    absent_today = today_records.filter(status='absent').count()
    tardy_today = today_records.filter(status='tardy').count()

    total_today = today_records.count()
    attendance_percentage = (present_today / total_today * 100) if total_today > 0 else 0

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_classrooms': total_classrooms,
        'present_today': present_today,
        'absent_today': absent_today,
        'tardy_today': tardy_today,
        'attendance_percentage': round(attendance_percentage, 1),
    }

    return render(request, 'core/dashboard.html', context)


# -------------------------
# STUDENTS
# -------------------------
def student_list(request):
    students = Student.objects.all()
    return render(request, 'core/student_list.html', {'students': students})


def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    attendance_records = Attendance.objects.filter(student=student).order_by('-date')

    present = attendance_records.filter(status='present').count()
    absent = attendance_records.filter(status='absent').count()
    tardy = attendance_records.filter(status='tardy').count()

    context = {
        'student': student,
        'attendance_records': attendance_records,
        'present': present,
        'absent': absent,
        'tardy': tardy,
    }

    return render(request, 'core/student_detail.html', context)


def create_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()

            # If a password was generated, show it
            password = getattr(student, "generated_password", None)

            return render(request, "core/student_created.html", {
                "student": student,
                "password": password,
            })

    else:
        form = StudentForm()

    return render(request, 'core/create_student.html', {'form': form})



def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_detail', pk=pk)
    else:
        form = StudentForm(instance=student)

    return render(request, 'core/edit_student.html', {'form': form, 'student': student})


def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        student.delete()
        return redirect('student_list')

    return render(request, 'core/delete_student.html', {'student': student})


def remove_student_photo(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if student.photo:
        if os.path.isfile(student.photo.path):
            os.remove(student.photo.path)

        student.photo = None
        student.save()

    return redirect('edit_student', pk=pk)


def upload_student_photo(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST' and request.FILES.get('photo'):
        if student.photo:
            student.photo.delete()

        student.photo = request.FILES['photo']
        student.save()

        return redirect('student_detail', pk=pk)

    return redirect('student_detail', pk=pk)


# -------------------------
# STUDENT REPORT PDF
# -------------------------
def student_report_pdf(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    report_period = "Quarter 1"
    school_year = "2025–2026"

    if student.classroom and student.classroom.teacher:
        teacher = student.classroom.teacher
        teacher_name = teacher.user.get_full_name()
    else:
        teacher_name = "—"

    principal_name = "Dr. Amanda Reynolds"
    principal_title = "School Principal"

    attendance_records = Attendance.objects.filter(student=student)
    present = attendance_records.filter(status="Present").count()
    absent = attendance_records.filter(status="Absent").count()
    tardy = attendance_records.filter(status="Tardy").count()

    qr_url = request.build_absolute_uri(f"/students/{student.id}/")
    qr = qrcode.make(qr_url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    context = {
        "student": student,
        "attendance_records": attendance_records,
        "present": present,
        "absent": absent,
        "tardy": tardy,
        "report_period": report_period,
        "school_year": school_year,
        "teacher_name": teacher_name,
        "principal_name": principal_name,
        "principal_title": principal_title,
        "qr_code": qr_base64,
    }

    template_path = "core/student_report.html"
    html = render_to_string(template_path, context)
    response = HttpResponse(content_type="application/pdf")
    pisa.CreatePDF(html, dest=response)

    return response


# -------------------------
# TEACHERS
# -------------------------
def teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, 'core/teacher_list.html', {'teachers': teachers})


def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    classroom = Classroom.objects.filter(teacher=teacher).first()
    students = Student.objects.filter(classroom=classroom) if classroom else []

    return render(request, 'core/teacher_detail.html', {
        'teacher': teacher,
        'classroom': classroom,
        'students': students,
    })


def create_teacher(request):
    if request.method == 'POST':
        first = request.POST.get('first_name')
        last = request.POST.get('last_name')
        username = request.POST.get('username')
        subject = request.POST.get('subject')

        user = User.objects.create(username=username, first_name=first, last_name=last)
        Teacher.objects.create(user=user, subject=subject)

        return redirect('teacher_list')

    return render(request, 'core/create_teacher.html')


def edit_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)

    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect('teacher_detail', pk=pk)
    else:
        form = TeacherForm(instance=teacher)

    return render(request, 'core/edit_teacher.html', {'form': form, 'teacher': teacher})


def delete_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)

    if request.method == 'POST':
        teacher.delete()
        return redirect('teacher_list')

    return render(request, 'core/delete_teacher.html', {'teacher': teacher})


# -------------------------
# CLASSROOMS
# -------------------------
def classroom_list(request):
    classrooms = Classroom.objects.all()
    return render(request, 'core/classroom_list.html', {'classrooms': classrooms})


def classroom_detail(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)

    students = Student.objects.filter(classroom=classroom)
    all_students = Student.objects.all()
    assignments = Assignment.objects.filter(classroom=classroom).order_by('-date_assigned')

    # -----------------------------
    # CLASS AVERAGE
    # -----------------------------
    grades = Grade.objects.filter(assignment__classroom=classroom)

    if grades.exists():
        total_points_earned = sum((g.points_earned or 0) for g in grades)
        total_points_possible = sum((g.assignment.points_possible or 0) for g in grades)

        class_average_percent = (
            (total_points_earned / total_points_possible) * 100
            if total_points_possible > 0 else 0
        )
    else:
        class_average_percent = None

    # -----------------------------
    # PER‑ASSIGNMENT AVERAGES
    # -----------------------------
    assignment_averages = []
    for assignment in assignments:
        ag = Grade.objects.filter(assignment=assignment)

        if ag.exists():
            total_earned = sum((g.points_earned or 0) for g in ag)
            total_possible = (assignment.points_possible or 0) * ag.count()
            avg_percent = (total_earned / total_possible) * 100 if total_possible > 0 else 0
        else:
            avg_percent = None

        assignment_averages.append({
            "assignment": assignment,
            "average_percent": avg_percent,
        })

    # -----------------------------
    # PER‑STUDENT AVERAGES
    # -----------------------------
    student_averages = []
    for student in students:
        sg = Grade.objects.filter(student=student, assignment__classroom=classroom)

        if sg.exists():
            earned = sum((g.points_earned or 0) for g in sg)
            possible = sum((g.assignment.points_possible or 0) for g in sg)
            avg_percent = (earned / possible) * 100 if possible > 0 else 0
        else:
            avg_percent = None

        student_averages.append({
            "student": student,
            "average_percent": avg_percent,
        })

    # -----------------------------
    # MISSING ASSIGNMENTS + COUNTS
    # -----------------------------
    missing_assignments = []
    for student in students:
        student_missing = []
        for assignment in assignments:
            has_grade = Grade.objects.filter(student=student, assignment=assignment).exists()
            if not has_grade:
                student_missing.append(assignment)

        missing_assignments.append({
            "student": student,
            "missing": student_missing,
            "count": len(student_missing),
        })

    total_missing = sum(item["count"] for item in missing_assignments)

    top_missing_students = sorted(
        missing_assignments,
        key=lambda x: x["count"],
        reverse=True
    )[:3]

    return render(request, 'core/classroom_detail.html', {
        "classroom": classroom,
        "students": students,
        "all_students": all_students,
        "assignments": assignments,
        "assignment_averages": assignment_averages,
        "student_averages": student_averages,
        "missing_assignments": missing_assignments,
        "total_missing": total_missing,
        "top_missing_students": top_missing_students,
        "class_average_percent": class_average_percent,
        "today": date.today(),
    })


def create_classroom(request):
    teachers = Teacher.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        teacher_id = request.POST.get('teacher_id')

        Classroom.objects.create(name=name, teacher_id=teacher_id)
        return redirect('classroom_list')

    return render(request, 'core/create_classroom.html', {'teachers': teachers})


def edit_classroom(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    teachers = Teacher.objects.all()

    if request.method == 'POST':
        classroom.name = request.POST.get('name')
        classroom.teacher_id = request.POST.get('teacher_id')
        classroom.save()
        return redirect('classroom_detail', pk=pk)

    return render(request, 'core/edit_classroom.html', {
        'classroom': classroom,
        'teachers': teachers
    })


def delete_classroom(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)

    if request.method == 'POST':
        classroom.delete()
        return redirect('classroom_list')

    return render(request, 'core/delete_classroom.html', {'classroom': classroom})


def add_student_to_classroom(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student = get_object_or_404(Student, pk=student_id)
        student.classroom = classroom
        student.save()

    return redirect('classroom_detail', pk=pk)


def remove_student_from_classroom(request, classroom_pk, student_pk):
    student = get_object_or_404(Student, pk=student_pk)
    student.classroom = None
    student.save()

    return redirect('classroom_detail', pk=classroom_pk)


# -------------------------
# ATTENDANCE
# -------------------------
def take_attendance(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    students = Student.objects.filter(classroom=classroom)

    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f"status_{student.pk}")
            Attendance.objects.update_or_create(
                student=student,
                classroom=classroom,
                date=date.today(),
                defaults={'status': status}
            )
        return redirect('classroom_detail', pk=pk)

    return render(request, 'core/take_attendance.html', {
        'classroom': classroom,
        'students': students,
        'today': date.today(),
    })


def classroom_attendance_history(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    attendance_records = Attendance.objects.filter(classroom=classroom).order_by('-date')

    return render(request, 'core/classroom_attendance_history.html', {
        'classroom': classroom,
        'attendance_records': attendance_records,
    })


def student_attendance_history(request, pk):
    student = get_object_or_404(Student, pk=pk)
    attendance_records = Attendance.objects.filter(student=student).order_by('-date')

    return render(request, 'core/student_attendance_history.html', {
        'student': student,
        'attendance_records': attendance_records,
    })


def classroom_attendance_summary(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    summary = classroom.attendance_summary

    return render(request, 'core/classroom_attendance_summary.html', {
        'classroom': classroom,
        'summary': summary,
    })


def student_attendance_summary(request, pk):
    student = get_object_or_404(Student, pk=pk)
    summary = student.attendance_summary

    return render(request, 'core/student_attendance_summary.html', {
        'student': student,
        'summary': summary,
    })


# -------------------------
# ASSIGNMENTS & GRADES
# -------------------------
def assignment_list(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    assignments = Assignment.objects.filter(classroom=classroom).order_by("-date_assigned")

    students = classroom.student_set.all()
    total_students = students.count()

    assignment_data = []

    for a in assignments:
        graded = Grade.objects.filter(assignment=a, points_earned__isnull=False).count()
        missing = Grade.objects.filter(assignment=a, is_missing=True).count()
        ungraded = total_students - graded - missing

        if total_students > 0:
            pct_graded = (graded / total_students) * 100
            pct_missing = (missing / total_students) * 100
            pct_ungraded = (ungraded / total_students) * 100
        else:
            pct_graded = pct_missing = pct_ungraded = 0

        assignment_data.append({
            "assignment": a,
            "graded": graded,
            "missing": missing,
            "ungraded": ungraded,
            "pct_graded": pct_graded,
            "pct_missing": pct_missing,
            "pct_ungraded": pct_ungraded,
            "total_students": total_students,   # ← THIS FIXES YOUR ERROR
        })

    return render(request, "core/assignment_list.html", {
        "classroom": classroom,
        "assignments": assignment_data,
    })



class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["title", "subject", "description", "date_assigned", "date_due", "points_possible"]


def add_assignment(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)

    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.classroom = classroom   # ⭐ CRITICAL LINE
            assignment.save()

            # Create Grade rows
            for student in classroom.student_set.all():
                Grade.objects.get_or_create(
                    assignment=assignment,
                    student=student,
                    defaults={'points_earned': None}
                )

            return redirect("assignment_detail", pk=assignment.pk)

    else:
        form = AssignmentForm()

    return render(request, "core/add_assignment.html", {
        "form": form,
        "classroom": classroom,
    })








def enter_grades(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    students = Student.objects.filter(classroom=assignment.classroom)

    existing = {
        g.student_id: g.points_earned
        for g in Grade.objects.filter(assignment=assignment)
    }

    for student in students:
        student.grade_value = existing.get(student.id, "")

    if request.method == "POST":
        for student in students:
            field_name = f"grade_{student.id}"
            points = request.POST.get(field_name)

            if points is not None and points != "":
                points = int(points)

                grade, created = Grade.objects.get_or_create(
                    student=student,
                    assignment=assignment,
                    defaults={"points_earned": points},
                )

                if not created:
                    grade.points_earned = points
                    grade.save()

        return redirect("assignment_list", classroom_id=assignment.classroom.id)

    return render(request, "core/enter_grades.html", {
        "assignment": assignment,
        "students": students,
    })


def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    students = assignment.classroom.student_set.all()

    grade_map = {
        g.student_id: g
        for g in Grade.objects.filter(assignment=assignment)
    }

    grade_list = []
    for student in students:
        grade = grade_map.get(student.id)

        if grade:
            points_earned = grade.points_earned
            percent = (
                (grade.points_earned / assignment.points_possible) * 100
                if grade.points_earned is not None and assignment.points_possible
                else None
            )
            is_missing = grade.is_missing
        else:
            points_earned = None
            percent = None
            is_missing = False

        grade_list.append({
            "student": student,
            "points_earned": points_earned,
            "percent": percent,
            "is_missing": is_missing,
        })

    return render(request, 'core/assignment_detail.html', {
        "assignment": assignment,
        "grades": grade_list,
    })


def enter_grade(request, assignment_id, student_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    student = get_object_or_404(Student, pk=student_id)

    grade, created = Grade.objects.get_or_create(
        assignment=assignment,
        student=student
    )

    if request.method == "POST":
        points = request.POST.get("points_earned")
        grade.points_earned = points
        grade.save()
        return redirect("assignment_detail", pk=assignment_id)

    return render(request, "core/enter_grade.html", {
        "assignment": assignment,
        "student": student,
        "grade": grade,
    })


def mark_missing(request, assignment_id, student_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    student = get_object_or_404(Student, pk=student_id)

    grade, created = Grade.objects.get_or_create(
        assignment=assignment,
        student=student
    )

    grade.is_missing = True
    grade.points_earned = None
    grade.save()

    return redirect('assignment_detail', pk=assignment_id)


def update_grade(request, assignment_id, student_id):
    if request.method == "POST":
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        student = get_object_or_404(Student, pk=student_id)

        grade, created = Grade.objects.get_or_create(
            assignment=assignment,
            student=student
        )

        new_points = request.POST.get("points")

        if new_points == "":
            grade.points_earned = None
        else:
            grade.points_earned = int(new_points)

        grade.is_missing = False
        grade.save()

        return JsonResponse({
            "success": True,
            "percent": grade.points_earned / assignment.points_possible * 100
                if grade.points_earned is not None and assignment.points_possible else None
        })

    return JsonResponse({"success": False}, status=400)

from django.contrib.auth.decorators import login_required

@login_required
def teacher_portal(request):
    if not hasattr(request.user, "teacher"):
        return redirect("home")

    teacher = request.user.teacher
    classrooms = Classroom.objects.filter(teacher=teacher)

    return render(request, "core/teacher_portal.html", {
        "teacher": teacher,
        "classrooms": classrooms,
    })


@login_required
def teacher_dashboard(request):
    if not hasattr(request.user, "teacher"):
        return redirect("home")

    teacher = request.user.teacher
    classrooms = Classroom.objects.filter(teacher=teacher)

    total_students = Student.objects.filter(classroom__teacher=teacher).count()
    total_assignments = Assignment.objects.filter(classroom__teacher=teacher).count()

    recent_assignments = Assignment.objects.filter(
        classroom__teacher=teacher
    ).order_by("-date_assigned")[:5]

    today = date.today()
    today_attendance = Attendance.objects.filter(
        classroom__teacher=teacher,
        date=today
    )

    present = today_attendance.filter(status="present").count()
    absent = today_attendance.filter(status="absent").count()
    tardy = today_attendance.filter(status="tardy").count()

    return render(request, "teacher/dashboard.html"), {
        "teacher": teacher,
        "classrooms": classrooms,
        "total_students": total_students,
        "total_assignments": total_assignments,
        "recent_assignments": recent_assignments,
        "present": present,
        "absent": absent,
        "tardy": tardy,
        "today": today,
    }

from django.contrib.auth.decorators import login_required

@login_required
def student_portal(request):
    # Make sure the logged-in user *is* a student
    if not hasattr(request.user, "student"):
        return redirect("home")

    student = request.user.student
    classroom = student.classroom

    # Attendance
    attendance_records = Attendance.objects.filter(student=student)
    present = attendance_records.filter(status="present").count()
    absent = attendance_records.filter(status="absent").count()
    tardy = attendance_records.filter(status="tardy").count()

    # Assignments
    assignments = Assignment.objects.filter(classroom=classroom).order_by("-date_assigned")

    grade_map = {
        g.assignment_id: g
        for g in Grade.objects.filter(student=student)
    }

    assignment_list = []
    for a in assignments:
        grade = grade_map.get(a.id)

        if grade:
            percent = (
                (grade.points_earned / a.points_possible) * 100
                if grade.points_earned is not None and a.points_possible
                else None
            )
            is_missing = grade.is_missing
        else:
            percent = None
            is_missing = True  # no grade = missing

        assignment_list.append({
            "assignment": a,
            "grade": grade.points_earned if grade else None,
            "percent": percent,
            "is_missing": is_missing,
        })

    # Student average
    student_grades = Grade.objects.filter(student=student)
    if student_grades.exists():
        earned = sum((g.points_earned or 0) for g in student_grades)
        possible = sum((g.assignment.points_possible or 0) for g in student_grades)
        student_average = (earned / possible) * 100 if possible > 0 else 0
    else:
        student_average = None

    return render(request, "core/student_portal.html", {
        "student": student,
        "classroom": classroom,
        "assignments": assignment_list,
        "present": present,
        "absent": absent,
        "tardy": tardy,
        "student_average": student_average,
    })

from django.shortcuts import redirect

def portal_redirect(request):
    user = request.user

    # Admins must go to the admin dashboard
    if user.is_superuser:
        return redirect("/admin/")

    # Teacher portal
    if hasattr(user, "teacher"):
        return redirect("teacher_portal")

    # Parent portal
    if hasattr(user, "parent"):
        return redirect("parent_portal")

    # Student portal (optional)
    if hasattr(user, "student"):
        return redirect("student_portal")

    # Fallback if no role is found
    return redirect("/")


from .models import Parent, Student, Grade, Assignment, Attendance

@login_required
def parent_portal(request):
    # Make sure the logged-in user is a parent
    if not hasattr(request.user, "parent"):
        return redirect("home")

    parent = request.user.parent
    children = parent.students.all()

    child_data = []

    for child in children:
        # Attendance summary
        attendance = Attendance.objects.filter(student=child)
        present = attendance.filter(status="present").count()
        absent = attendance.filter(status="absent").count()
        tardy = attendance.filter(status="tardy").count()

        # Grades
        grades = Grade.objects.filter(student=child)
        assignments = Assignment.objects.filter(classroom=child.classroom)

        assignment_list = []
        for a in assignments:
            grade = grades.filter(assignment=a).first()

            if grade:
                percent = (
                    (grade.points_earned / a.points_possible) * 100
                    if grade.points_earned is not None and a.points_possible
                    else None
                )
                is_missing = grade.is_missing
            else:
                percent = None
                is_missing = True

            assignment_list.append({
                "assignment": a,
                "grade": grade.points_earned if grade else None,
                "percent": percent,
                "is_missing": is_missing,
            })

        child_data.append({
            "student": child,
            "attendance": {
                "present": present,
                "absent": absent,
                "tardy": tardy,
            },
            "assignments": assignment_list,
        })

    return render(request, "core/parent_portal.html", {
        "parent": parent,
        "children": child_data,
    })

def create_parent(request):
    if request.method == 'POST':
        form = ParentForm(request.POST)
        if form.is_valid():
            parent = form.save()

            password = getattr(parent, "generated_password", None)

            return render(request, "core/parent_created.html", {
                "parent": parent,
                "password": password,
            })

    else:
        form = ParentForm()

    return render(request, "core/create_parent.html", {'form': form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseForbidden

from .models import Teacher, Parent, Student, Classroom, Assignment
from .utils import is_teacher, is_parent


# ---------------------------------------------------------
# TEACHER DASHBOARD
# ---------------------------------------------------------
@login_required
def teacher_dashboard(request):
    if not is_teacher(request.user):
        return HttpResponseForbidden("Not authorized.")

    teacher = Teacher.objects.get(user=request.user)
    classrooms = Classroom.objects.filter(teacher=teacher)
    assignments = Assignment.objects.filter(classroom__teacher=teacher)

    return render(request, "teacher/dashboard.html", {
        "teacher": teacher,
        "classrooms": classrooms,
        "assignments": assignments,
    })


# ---------------------------------------------------------
# PARENT DASHBOARD
# ---------------------------------------------------------
@login_required
def parent_dashboard(request):
    if not is_parent(request.user):
        return HttpResponseForbidden("Not authorized.")

    parent = Parent.objects.get(user=request.user)
    students = parent.students.all()
    assignments = Assignment.objects.filter(
        classroom__students__in=students
    ).distinct()

    return render(request, "parent/dashboard.html", {
        "parent": parent,
        "students": students,
        "assignments": assignments,
    })

def manage_students(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    all_students = Student.objects.all()

    if request.method == "POST":
        selected_ids = request.POST.getlist("students")

        # Remove students who were previously in this classroom
        Student.objects.filter(classroom=classroom).update(classroom=None)

        # Add selected students to this classroom
        Student.objects.filter(id__in=selected_ids).update(classroom=classroom)

        return redirect("classroom_detail", pk=classroom.id)

    return render(request, "core/manage_students.html", {
        "classroom": classroom,
        "all_students": all_students,
    })

def backfill_grades(request):
    for assignment in Assignment.objects.all():
        classroom = assignment.classroom
        if not classroom:
            continue

        students = classroom.student_set.all()

        for student in students:
            Grade.objects.get_or_create(
                assignment=assignment,
                student=student,
                defaults={'points_earned': None}
            )

    return HttpResponse("Backfill complete.")

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Assignment

def delete_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    classroom_id = assignment.classroom.id

    assignment.delete()
    messages.success(request, "Assignment deleted successfully.")

    return redirect("assignment_list", classroom_id)

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Classroom

def delete_classroom(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)

    # Optional: permission check
    # if request.user != classroom.teacher.user:
    #     messages.error(request, "You do not have permission to delete this classroom.")
    #     return redirect("classroom_detail", pk)

    classroom.delete()
    messages.success(request, "Classroom deleted successfully.")
    return redirect("classroom_list")
