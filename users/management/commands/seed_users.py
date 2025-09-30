from django.core.management.base import BaseCommand
from users.models import User, Profile

class Command(BaseCommand):
    help = 'Seed the database with initial users (student, professor, admin)'

    def handle(self, *args, **kwargs):
        if User.objects.exists():
            self.stdout.write(self.style.WARNING('Users already exist. Skipping seeding.'))
            return

        # Admin
        admin_user = User.objects.create_superuser(
            email='admin@university.com',
            password='Admin123!',
            first_name='Alice',
            last_name='Admin'
        )
        Profile.objects.create(user=admin_user, bio='Administrator of the CMS')

        # Professor
        professor_user = User.objects.create_user(
            email='professor@university.com',
            password='Professor123!',
            first_name='Bob',
            last_name='Professor',
            role=User.Role.EDITOR  # or AUTHOR depending on your CMS logic
        )
        Profile.objects.create(user=professor_user, bio='Computer Science Professor')

        # Student
        student_user = User.objects.create_user(
            email='student@university.com',
            password='Student123!',
            first_name='Charlie',
            last_name='Student',
            role=User.Role.VIEWER
        )
        Profile.objects.create(user=student_user, bio='Enrolled Computer Science Student')

        self.stdout.write(self.style.SUCCESS('Successfully seeded users!'))

