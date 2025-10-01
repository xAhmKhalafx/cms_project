## Quick Start
1. Create and activate venv
2. pip install -r requirements.txt
3. python manage.py migrate
4. python manage.py createsuperuser   # or loaddata users_seed if you keep auth fixtures
5. python manage.py loaddata roles_seed courses_seed assignments_seed
6. python manage.py runserver
