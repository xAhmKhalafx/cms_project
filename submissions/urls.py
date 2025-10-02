from django.urls import path
from .views import submit_assignment_page, list_submissions_page, grade_submission_page

urlpatterns = [
    path('assignments/<int:assignment_id>/submit/', submit_assignment_page, name='submission-create-page'),
    path('assignments/<int:assignment_id>/submissions/', list_submissions_page, name='submissions-list-page'),
    path('submissions/<int:submission_id>/grade/', grade_submission_page, name='submission-grade-page'),
]
