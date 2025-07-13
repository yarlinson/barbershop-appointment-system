import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barbershop.settings')
django.setup()

from django.contrib.auth.hashers import make_password

passwords = {
    'admin': make_password('admin2024'),
    'carlos': make_password('barbero2024'),
    'juan': make_password('barbero2024'),
    'pedro': make_password('cliente2024')
}

print("\nContraseñas hasheadas para MySQL:")
print("----------------------------------")
for user, password in passwords.items():
    print(f"\n-- Contraseña para {user}:")
    print(f"'{password}',") 