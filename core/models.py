from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    parent_name = models.CharField(max_length=200, null=True, blank=True)
    parent_phone = models.CharField(max_length=20, null=True, blank=True)
    parent_email = models.EmailField(null=True, blank=True)
    photo = models.ImageField(upload_to='student_photos/', null=True, blank=True)
    classroom = models.ForeignKey('Classroom', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def attendance_summary(self):
        records = Attendance.objects.filter(student=self)
        total = records.count()

        present = records.filter(status='present').count()
        absent = records.filter(status='absent').count()
        tardy = records.filter(status='tardy').count()

        percentage = (present / total * 100) if total > 0 else 0

        return {
            'total': total,
            'present': present,
            'absent': absent,
            'tardy': tardy,
            'percentage': round(percentage, 1),
        }



class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)

    class Meta:
        ordering = ['user__first_name']

    def __str__(self):
        return self.user.get_full_name()


class Classroom(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True, blank=True)
    students = models.ManyToManyField('Student', related_name='classrooms', blank=True)

    def __str__(self):
        return self.name
    
    def auto_enroll_all_students(self):
        from core.models import Student
        for student in Student.objects.all():
            self.students.add(student)


    @property
    def attendance_summary(self):
        records = Attendance.objects.filter(classroom=self)
        total = records.count()

        present = records.filter(status='present').count()
        absent = records.filter(status='absent').count()
        tardy = records.filter(status='tardy').count()

        percentage = (present / total * 100) if total > 0 else 0

        return {
            'total': total,
            'present': present,
            'absent': absent,
            'tardy': tardy,
            'percentage': round(percentage, 1),
        }



class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('tardy', 'Tardy'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"

class Assignment(models.Model):
    SUBJECT_CHOICES = [
        ("Reading", "Reading"),
        ("Math", "Math"),
        ("Writing", "Writing"),
        ("Science", "Science"),
        ("Social Studies", "Social Studies"),
    ]

    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    description = models.TextField(blank=True)
    date_assigned = models.DateField()
    date_due = models.DateField()
    points_possible = models.IntegerField(default=100)

    def __str__(self):
        return f"{self.title} ({self.subject})"



class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    points_earned = models.IntegerField(null=True, blank=True)
    is_missing = models.BooleanField(default=False)

    class Meta:
        unique_together = ("student", "assignment")

from django.contrib.auth.models import User

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    students = models.ManyToManyField('Student', related_name='parents')

    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


