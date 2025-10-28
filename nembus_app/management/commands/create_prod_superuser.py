# nembus_app/management/commands/create_prod_superuser.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os # Necesario para leer variables de entorno (opcional pero recomendado)

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea un superusuario si no existe uno con el nombre de usuario especificado.'

    def handle(self, *args, **options):
        # --- DEFINE AQUÍ LOS DATOS DE TU SUPERUSUARIO ---
        # Puedes usar variables de entorno o ponerlos directamente
        # ¡Usa una contraseña segura!
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin_render') # Nombre de usuario deseado
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com') # Email (opcional, puedes dejarlo vacío '')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'contraseña_segura_aqui') # CONTRASEÑA SEGURA

        if not password:
             self.stdout.write(self.style.ERROR('Error: La contraseña del superusuario no está configurada (DJANGO_SUPERUSER_PASSWORD).'))
             return # Salir si no hay contraseña

        if not User.objects.filter(username=username).exists():
            self.stdout.write(f"Creando superusuario '{username}'...")
            try:
                User.objects.create_superuser(username=username, email=email, password=password)
                self.stdout.write(self.style.SUCCESS(f"Superusuario '{username}' creado exitosamente."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error al crear superusuario: {e}"))
        else:
            self.stdout.write(self.style.WARNING(f"El superusuario '{username}' ya existe. No se realizaron cambios."))