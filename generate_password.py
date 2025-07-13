from django.contrib.auth.hashers import make_password

passwords = {
    'admin': make_password('admin2024'),
    'carlos': make_password('barbero2024'),
    'juan': make_password('barbero2024'),
    'pedro': make_password('cliente2024')
}

for user, password in passwords.items():
    print(f"-- Password for {user}: {password}") 