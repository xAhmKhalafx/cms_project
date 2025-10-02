from django import forms
from .models import Assignment

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["course", "title", "description", "due_date"]
        labels = {
            "course": "Course",
            "title": "Title",
            "description": "Description",
            "due_date": "Due date"
        }
        widgets = {
            "course": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"placeholder": "e.g. Project Proposal"}),
            "description": forms.Textarea(attrs={"placeholder": "Brief description / requirements", "rows": 4}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }
