from django import forms
from django.contrib.auth.models import User
from .models import Student, Lecturer

class UserBaseForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Set an initial password"}),
        required=True,
        label="Password"
    )
    role = forms.ChoiceField(
        choices=[('student','Student'), ('lecturer','Lecturer')],
        required=True,
        label="Role"
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password"]
        labels = {
            "username": "Username",
            "first_name": "First name",
            "last_name": "Last name",
            "email": "Email"
        }
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "e.g. jdoe23"}),
            "first_name": forms.TextInput(attrs={"placeholder": "e.g. Jane"}),
            "last_name": forms.TextInput(attrs={"placeholder": "e.g. Doe"}),
            "email": forms.EmailInput(attrs={"placeholder": "e.g. jdoe@university.edu"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make these optional to reduce friction (you can enforce later if needed)
        self.fields["first_name"].required = False
        self.fields["last_name"].required = False
        self.fields["email"].required = False


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active", "is_staff"]
        labels = {
            "username": "Username",
            "first_name": "First name",
            "last_name": "Last name",
            "email": "Email",
            "is_active": "Active",
            "is_staff": "Staff (console access)"
        }
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "e.g. jdoe23"}),
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
        }


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["student_number", "program"]
        labels = {"student_number": "Student number", "program": "Program"}
        widgets = {
            "student_number": forms.TextInput(attrs={"placeholder": "e.g. STU200123"}),
            "program": forms.TextInput(attrs={"placeholder": "e.g. Software Engineering"}),
        }


class LecturerForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ["employee_number", "department"]
        labels = {"employee_number": "Employee number", "department": "Department"}
        widgets = {
            "employee_number": forms.TextInput(attrs={"placeholder": "e.g. LEC001122"}),
            "department": forms.TextInput(attrs={"placeholder": "e.g. IT / Computing"}),
        }
