from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = 'Создаёт или обновляет суперпользователя admin / admin123'

    def handle(self, *args, **options):
        user, _created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@green-cafe-str.ru'},
        )

        # Явно приводим пользователя к ожидаемому состоянию.
        user.email = user.email or 'admin@green-cafe-str.ru'
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password('admin123')
        user.save(
            update_fields=[
                'password',
                'email',
                'is_active',
                'is_staff',
                'is_superuser',
            ]
        )

        self.stdout.write(self.style.SUCCESS('Гарантированно выставлен admin / admin123'))
