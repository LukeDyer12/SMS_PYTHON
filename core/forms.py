from django import forms
from .models import Student, Teacher, Classroom, Parent, Assignment


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'first_name',
            'last_name',
            'date_of_birth',
            'parent_name',
            'parent_phone',
            'parent_email',
            'photo',          
            'classroom',
        ]



class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['subject']

class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['name']


class ParentForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = ['first_name', 'last_name', 'email', 'phone', 'students']
        widgets = {
            'students': forms.CheckboxSelectMultiple()
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'subject', 'description', 'date_assigned', 'date_due', 'points_possible']

        
