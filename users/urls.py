from django.urls import path
from .views import dashboard, user_login, user_logout, console_home, help_docs
from . import console_views

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('help/', help_docs, name='help-docs'),

    path('console/', console_home, name='console-home'),
    path('accounts/login/', user_login, name='accounts-login'),

    # USERS CRUD in console
    path('console/users/', console_views.users_list, name='console-users-list'),
    path('console/users/new/', console_views.users_create, name='console-users-create'),
    path('console/users/<int:user_id>/edit/', console_views.users_edit, name='console-users-edit'),
    path('console/users/<int:user_id>/delete/', console_views.users_delete, name='console-users-delete'),
]
