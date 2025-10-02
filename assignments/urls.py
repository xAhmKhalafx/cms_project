from django.urls import path
from .views import create_assignment_page  # (your public page)
from . import console_views

urlpatterns = [
    # public UI route
    path('courses/<int:course_id>/assignments/new/', create_assignment_page, name='assignment-create-page'),

    # console CRUD
    path('console/assignments/', console_views.assignments_list, name='console-assignments-list'),
    path('console/assignments/new/', console_views.assignments_create, name='console-assignments-create'),
    path('console/assignments/<int:assignment_id>/edit/', console_views.assignments_edit, name='console-assignments-edit'),
    path('console/assignments/<int:assignment_id>/delete/', console_views.assignments_delete, name='console-assignments-delete'),
]
