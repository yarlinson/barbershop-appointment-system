# Sistema de Gestión de Citas para Barbería

Sistema web para la gestión de citas y servicios de barbería, desarrollado con Django, MySQL y React.

## 🚀 Descripción del Proyecto

Este sistema permite a los clientes agendar citas con sus barberos preferidos, gestionar servicios y mantener un registro organizado de las citas. Está diseñado para optimizar la gestión de tiempo tanto para barberos como para clientes.

### 🎯 Características Principales

- Gestión de usuarios (Clientes, Barberos, Administradores)
- Registro y gestión de servicios
- Sistema de citas con confirmación
- Horarios personalizados por barbero
- Panel administrativo completo
- API REST para integración con frontend

### 🛠️ Tecnologías Utilizadas

- **Backend:**
  - Django 5.2.4
  - Django REST Framework 3.14.0
  - MySQL 8.0
  - JWT para autenticación

- **Frontend (En desarrollo):**
  - React (próximamente)
  - Material-UI (próximamente)

- **Herramientas:**
  - Docker y Docker Compose
  - Git para control de versiones

## 📋 Prerrequisitos

### Método 1: Con Docker (Recomendado)
- Docker Desktop
- Docker Compose

### Método 2: Instalación Local
- Python 3.11 o superior
- MySQL 8.0
- Pip (gestor de paquetes de Python)
- Entorno virtual de Python (venv)

## 🔧 Instalación

### Método 1: Usando Docker (Recomendado)

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/sistema-citas-barberia.git
   cd sistema-citas-barberia
   ```

2. **Construir y levantar los contenedores**
   ```bash
   docker-compose up --build
   ```

3. **Aplicar las migraciones**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Crear un superusuario**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

La aplicación estará disponible en:
- Frontend: http://localhost:8000
- Panel Admin: http://localhost:8000/admin
- API: http://localhost:8000/api/

### Método 2: Instalación Local

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/sistema-citas-barberia.git
   cd sistema-citas-barberia
   ```

2. **Crear y activar entorno virtual**
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar la base de datos**
   ```sql
   CREATE DATABASE barbershop_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

5. **Configurar variables de entorno**
   Crear un archivo `.env` en la raíz del proyecto:
   ```env
   DEBUG=1
   DJANGO_SETTINGS_MODULE=barbershop.settings
   DATABASE_URL=mysql://newuser:+newuser+@localhost:3306/barbershop_db
   ```

6. **Aplicar migraciones**
   ```bash
   python manage.py migrate
   ```

7. **Crear superusuario**
   ```bash
   python manage.py createsuperuser
   ```

8. **Iniciar el servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

## 📦 Estructura del Proyecto

```
barbershop/
├── appointments/          # Aplicación principal
│   ├── models.py         # Modelos de datos
│   ├── admin.py          # Configuración del panel admin
│   └── ...
├── barbershop/           # Configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── static/               # Archivos estáticos
├── media/                # Archivos subidos por usuarios
├── Dockerfile           # Configuración de Docker
├── docker-compose.yml   # Configuración de servicios Docker
├── requirements.txt     # Dependencias del proyecto
└── manage.py
```

## 👥 Roles de Usuario

1. **Administrador**
   - Gestión completa del sistema
   - Acceso al panel administrativo
   - Gestión de usuarios y servicios

2. **Barbero**
   - Gestión de su disponibilidad
   - Ver y gestionar sus citas
   - Actualizar su perfil

3. **Cliente**
   - Agendar citas
   - Ver historial de citas
   - Gestionar su perfil

## 🔍 Solución de Problemas Comunes

### Problemas con Docker

1. **Error de permisos en el puerto 3306**
   - Detener cualquier instancia de MySQL local
   - Verificar que Docker Desktop esté ejecutándose como administrador

2. **Error de conexión a la base de datos**
   - Esperar unos segundos después de `docker-compose up` para que MySQL inicialice
   - Verificar las credenciales en el archivo `docker-compose.yml`

3. **Cambios no reflejados**
   - Reconstruir los contenedores: `docker-compose down && docker-compose up --build`

### Problemas con la Instalación Local

1. **Error de MySQL**
   - Verificar que MySQL esté corriendo
   - Comprobar las credenciales en `settings.py`

2. **Error en las migraciones**
   - Eliminar archivos de migraciones y recrearlos
   - Verificar la conexión a la base de datos

## 🔜 Próximas Características

- [ ] Integración con React
- [ ] Sistema de notificaciones
- [ ] Calificaciones y reseñas
- [ ] Panel de estadísticas

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE.md](LICENSE.md) para más detalles

## ✒️ Autor

* **Tu Nombre** - *Desarrollo Completo* - [Tu Usuario de GitHub]

## 🎁 Agradecimientos

* Comparte este proyecto con otros 📢
* Invita una cerveza 🍺 o un café ☕ a alguien del equipo
* Da las gracias públicamente 🤓 