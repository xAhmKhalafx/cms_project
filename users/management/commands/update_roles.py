# users/management/commands/fix_roles.py

from django.core.management.base import BaseCommand
from users.models import User # Ensure this path is correct

class Command(BaseCommand):
    help = 'Updates roles for existing users to match the dashboard logic.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Starting user role update for existing users..."))

        # 1. Update the admin role
        updated_admins = User.objects.filter(email='admin@university.com').update(role='ADMIN')
        self.stdout.write(self.style.SUCCESS(f"Updated {updated_admins} admin user(s) to 'ADMIN'."))

        # 2. Update the professor role to INSTRUCTOR
        updated_profs = User.objects.filter(email='professor@university.com').update(role='INSTRUCTOR')
        self.stdout.write(self.style.SUCCESS(f"Updated {updated_profs} professor user(s) to 'INSTRUCTOR'."))

        # 3. Update the student roles to STUDENT
        # Targeting both the initially seeded student and the one created via signup (stud1)
        updated_students = User.objects.filter(
            email__in=['student@university.com', 'stud1@gmail.com']
        ).update(role='STUDENT')
        self.stdout.write(self.style.SUCCESS(f"Updated {updated_students} student user(s) to 'STUDENT'."))

        self.stdout.write(self.style.SUCCESS('Role update complete. Test login now.'))