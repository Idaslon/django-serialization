import contextlib
import os
import subprocess
from django import setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "serialization.settings")
setup()


def get_all_files(path: str) -> []:
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return files


def remove_all_migrations():
    remove_specific_app_migrations('demo')
    remove_specific_app_migrations('serializer/tests')


def remove_specific_app_migrations(app_name):
    app_migrations = get_all_files(f'{app_name}/migrations/')

    for migration in app_migrations:
        if migration != '__init__.py':
            os.remove(f'./{app_name}/migrations/' + migration)


def remove_db():
    with contextlib.suppress(FileNotFoundError):
        os.remove('db.sqlite3')


def make_migrations():
    subprocess.run('python manage.py makemigrations')


def migrate():
    subprocess.run('python manage.py migrate')


def create_super_user():
    from django.contrib.auth.models import User

    User.objects.create_superuser('admin', '', '123')


remove_db()
remove_all_migrations()
make_migrations()
migrate()

create_super_user()
