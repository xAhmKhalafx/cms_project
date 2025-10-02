from django import forms
from django.contrib.auth.models import User
from .models import Student, Lecturer

class UserBaseForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    role = forms.ChoiceField(choices=[('student','Student'), ('lecturer','Lecturer')], required=True)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password"]

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active", "is_staff"]

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["student_number", "program"]

class LecturerForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ["employee_number", "department"]
