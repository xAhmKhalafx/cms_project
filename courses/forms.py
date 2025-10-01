from django import forms
# Import the date input widget to handle DateField correctly
from django.forms import DateInput 
from .models import Course, Assignment, Attendance # It's good practice to import all models used/needed
from users.models import User

# Form for creating/editing a Course
class CourseForm(forms.ModelForm):
    # Overwrite the default ManyToManyField for 'students' to improve the widget and queryset
    students = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role='student', is_deleted=False).order_by('last_name'),
        required=False,
        widget=forms.SelectMultiple(attrs={'size': 10}),
        help_text="Select students to enroll in this course."
    )
    
    class Meta:
        # 🟢 FIX 1: Change 'model' back to Course
        model = Course 
        fields = ['title', 'description', 'lecturer', 'students']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'lecturer': forms.Select(), 
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Further restrict the lecturer queryset to only active instructors
        self.fields['lecturer'].queryset = User.objects.filter(
            role='instructor', 
            is_active=True, 
            is_deleted=False
        ).order_by('last_name')
        
        # Add a helpful default option for the lecturer field
        self.fields['lecturer'].empty_label = "--- Select a Lecturer ---"

# 🟢 FIX 2: Add the missing AssignmentForm definition
class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        # Use the fields from your Assignment model
        fields = ['course', 'title', 'description', 'due_date'] 
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            # Use DateInput to make the due_date field user-friendly
            'due_date': DateInput(attrs={'type': 'date'}), 
        }