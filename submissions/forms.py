from django import forms
from .models import Submission

class AssessmentForm(forms.ModelForm):
    # Field to manually enter the grade
    grade = forms.DecimalField(
        label='Grade (Score)',
        max_digits=5,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '100'})
    )
    
    # Field for providing detailed feedback
    feedback = forms.CharField(
        label='Feedback / Comments',
        required=False,
        widget=forms.Textarea(attrs={'rows': 5})
    )
    
    class Meta:
        model = Submission
        # Only include fields related to the assessment process
        fields = ['grade', 'feedback'] 

    def save(self, commit=True):
        submission = super().save(commit=False)
        
        # Automatically update status if a grade is provided
        if submission.grade is not None:
            submission.status = 'graded'
        # If the grade is removed (set to null), revert status to pending
        elif submission.grade is None and submission.status == 'graded':
             submission.status = 'pending'
             
        if commit:
            submission.save()
        return submission
