from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Создаёт суперпользователя admin/admin'

    def handle(self, *args, **options):
        if User.objects.filter(username='admin').exists():
            self.stdout.write('Суперпользователь admin уже существует.')
            return
        User.objects.create_superuser('admin', 'admin@aromacoffee.ru', 'admin')
        self.stdout.write(self.style.SUCCESS('Создан admin / admin'))
