from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a user with an email and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # hashes the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a user with superuser privileges.
        Sets default role to ADMIN.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        # Use the correct TextChoice role for Admin
        extra_fields.setdefault("role", User.Role.ADMIN) 
        
        # Superuser must be active and not deleted
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_deleted", False)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for CMS/LMS.
    Email is used as the unique identifier.
    """
    # --- UPDATED ROLES FOR CMS/LMS ---
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        INSTRUCTOR = "INSTRUCTOR", "Instructor"
        STUDENT = "STUDENT", "Student"

    # --- FIX: Expose ROLE_CHOICES for use in forms.py ---
    @property
    def ROLE_CHOICES(self):
        """Returns the choices tuple in the format expected by forms."""
        return self.Role.choices
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=100) # Made required
    last_name = models.CharField(max_length=100)  # Made required
    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.STUDENT # Defaulting to the most common user type
    )

    # Django permission flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Soft delete flag
    is_deleted = models.BooleanField(default=False)
    
    # # --- LMS-SPECIFIC FIELD ADDED ---
    # enrolled_courses = models.ManyToManyField(
    #     'courses.Course', # String reference to Course model in the 'courses' app
    #     related_name='students',
    #     blank=True,
    #     help_text='The courses the student is currently enrolled in.'
    # )

    objects = UserManager()

    USERNAME_FIELD = "email"
    # Requiring first name and last name for user creation
    REQUIRED_FIELDS = ['first_name', 'last_name'] 

    def __str__(self):
        # Using the full_name property for a clearer display name
        return f"{self.full_name} ({self.role})" 

    @property
    def full_name(self):
        """Returns the first_name plus the last_name, with a space in between."""
        return f"{self.first_name} {self.last_name}".strip()
    
    # --- ROLE CHECKER METHODS ADDED ---
    def is_admin(self):
        """Checks if the user is an Administrator."""
        return self.role == self.Role.ADMIN
        
    def is_instructor(self):
        """Checks if the user is an Instructor."""
        return self.role == self.Role.INSTRUCTOR
        
    def is_student(self):
        """Checks if the user is a Student."""
        return self.role == self.Role.STUDENT

    def soft_delete(self):
        self.is_deleted = True
        self.is_active = False
        self.save()


class Profile(models.Model):
    """
    Extended profile for CMS user (kept from original structure).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    # Note: When using File/ImageFields, ensure your Django setup includes
    # a proper MEDIA_ROOT configuration and Pillow library installation.
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True) 
    website = models.URLField(blank=True)
    social_links = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Profile for {self.user.email}"
