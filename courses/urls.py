from django.urls import path
from .views import course_list_page, course_detail_page
from . import console_views

urlpatterns = [
    # public UI
    path('courses/', course_list_page, name='course-list-page'),
    path('courses/<int:course_id>/', course_detail_page, name='course-detail-page'),

    # console CRUD
    path('console/courses/', console_views.courses_manage_list, name='console-courses-list'),
    path('console/courses/new/', console_views.courses_create, name='console-courses-create'),
    path('console/courses/<int:course_id>/edit/', console_views.courses_edit, name='console-courses-edit'),
    path('console/courses/<int:course_id>/delete/', console_views.courses_delete, name='console-courses-delete'),
]
