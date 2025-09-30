# cms_project/urls.py
from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # User management API (optional if using DRF)
    path('api/users/', include('users.urls')),

    # Landing page
    path('', user_views.landing_page, name='landing'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),
    path('signup/', user_views.signup_page, name='signup'),

    # Dashboard
    path('dashboard/', user_views.dashboard_page, name='dashboard'),
]
