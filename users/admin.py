# users/admin.py
from django.contrib import admin
from .models import User, Profile
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "role", "is_staff", "is_active", "date_joined")
    list_filter  = ("role", "is_staff", "is_active")
    search_fields = ("email", "first_name", "last_name")
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bio")
