from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User # IMPORTANT: This assumes your custom User model is defined in users/models.py

class CustomUserCreationForm(UserCreationForm):
    """
    A form for creating a new user, including the 'role' field.
    Inherits standard password validation from UserCreationForm.
    """
    
    role = forms.ChoiceField(
        choices=User.Role.choices, 
        initial=User.Role.STUDENT,
        required=True,
        label="User Role",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # FIX: Explicitly specify fields to exclude 'username'.
        fields = ('email', 'first_name', 'last_name', 'role',) 

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Ensure email is unique across all users
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form for styling and presentation consistency."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

class AdminUserEditForm(forms.ModelForm):
    """Form used by Admin to edit user details, change roles, and manage course enrollments."""
    
    # This field is for managing the ManyToMany relationship
    enrolled_courses = forms.ModelMultipleChoiceField(
        queryset=None, # Set in __init__
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Enrolled Courses"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'is_active', 'is_deleted', 'enrolled_courses']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Deferred import to prevent circular dependency, specifically targeting the Course model.
        try:
            from courses.models import Course 
            self.fields['enrolled_courses'].queryset = Course.objects.all().order_by('title')
        except ImportError:
            # Fallback for when the courses app might not be fully loaded during Django's initial checks.
            print("Warning: Could not import Course model in users/forms.py init.")
            self.fields['enrolled_courses'].queryset = User.objects.none()

    def save(self, commit=True):
        """Custom save method to handle the ManyToMany relationship."""
        user = super().save(commit=False)
        if commit:
            user.save()
            # Handle ManyToMany field saving manually after the user object is saved
            if 'enrolled_courses' in self.cleaned_data:
                user.enrolled_courses.set(self.cleaned_data['enrolled_courses'])
        return user
