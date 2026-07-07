from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = 'Создаёт или обновляет суперпользователя admin / admin123'

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@green-cafe-str.ru',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        user.set_password('admin123')
        user.is_staff = True
        user.is_superuser = True
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS('Создан admin / admin123'))
        else:
            self.stdout.write(self.style.SUCCESS('Пароль admin обновлён на admin123'))
