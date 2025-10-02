from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),          # UI dashboards & auth
    path('', include('courses.urls')),        # UI pages (courses/assignments)
    path('', include('assignments.urls')),    # UI pages (forms)
    path('', include('submissions.urls')),    # UI pages (submit/grade)
    path('api/', include('courses.api_urls')),      # APIs
    path('api/', include('assignments.api_urls')),  # APIs
    path('api/', include('submissions.api_urls')),  # APIs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
