from django.contrib import admin
from django.urls import path
from courses import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/courses/', views.course_list),
]
