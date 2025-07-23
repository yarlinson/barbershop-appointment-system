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

5. **Asignar rol de administrador al superusuario**
   ```bash
   docker-compose exec web python manage.py shell -c "from appointments.models import User; user = User.objects.get(username='TU_USUARIO'); user.role = 'admin'; user.save()"
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

8. **Asignar rol de administrador al superusuario**
   ```bash
   python manage.py shell -c "from appointments.models import User; user = User.objects.get(username='TU_USUARIO'); user.role = 'admin'; user.save()"
   ```

9. **Iniciar el servidor de desarrollo**
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

* **Yarlinson Tiberio Barranco Bastilla** - *Desarrollo Completo* - [yarlinson]

## 🎁 Agradecimientos

## 📚 Documentación de la API

### Autenticación

Todos los endpoints requieren autenticación JWT. Incluir el token en el header:
```
Authorization: Bearer <token>
```

### Endpoints

#### Autenticación
- `POST /api/auth/register/` - Registro de usuarios
- `POST /api/auth/login/` - Inicio de sesión
- `POST /api/auth/login/refresh/` - Refrescar token
- `GET /api/auth/profile/` - Ver perfil
- `PUT /api/auth/profile/update/` - Actualizar perfil

#### Gestión de Barberos
- `GET /api/barbers/` - Listar todos los barberos
- `GET /api/barbers/{id}/` - Ver detalles de un barbero
- `POST /api/barbers/` - Crear nuevo barbero (solo admin)
- `PUT /api/barbers/{id}/` - Actualizar barbero (solo admin)
- `DELETE /api/barbers/{id}/` - Eliminar barbero (solo admin)

#### Horarios de Barberos
- `GET /api/barbers/{id}/schedules/` - Ver horarios de un barbero
- `POST /api/barbers/{id}/schedules/` - Agregar horario
```json
{
    "day_of_week": 0,
    "start_time": "09:00:00",
    "end_time": "17:00:00"
}
```
- `PUT /api/barbers/{id}/schedule/` - Actualizar horario
```json
{
    "schedule_id": 1,
    "start_time": "10:00:00",
    "end_time": "18:00:00"
}
```
- `DELETE /api/barbers/{id}/schedule/?schedule_id=1` - Eliminar horario

#### Gestión de Servicios
- `GET /api/services/` - Listar todos los servicios
- `GET /api/services/{id}/` - Ver detalles de un servicio
- `POST /api/services/` - Crear nuevo servicio (solo admin)
```json
{
    "name": "Corte de Cabello Clásico",
    "description": "Corte de cabello tradicional con tijeras y máquina",
    "price": "25.00",
    "duration": "00:30:00",
    "is_active": true
}
```
- `PUT /api/services/{id}/` - Actualizar servicio (solo admin)
- `DELETE /api/services/{id}/` - Eliminar servicio (solo admin)
- `PATCH /api/services/{id}/toggle_active/` - Activar/desactivar servicio (solo admin)

#### Gestión de Horarios
- `GET /api/schedules/` - Listar todos los horarios
- `GET /api/schedules/{id}/` - Ver detalle de horario
- `GET /api/schedules/{id}/?date=2024-03-20&duration=30` - Ver slots disponibles para una fecha
- `POST /api/schedules/` - Crear nuevo horario
```json
{
    "barber": 1,
    "day_of_week": 0,
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "interval_minutes": 30,
    "break_start_time": "13:00:00",
    "break_end_time": "14:00:00",
    "is_active": true
}
```
- `PUT /api/schedules/{id}/` - Actualizar horario
- `DELETE /api/schedules/{id}/` - Eliminar horario

#### Gestión de Excepciones de Horario
- `GET /api/schedule-exceptions/` - Listar todas las excepciones
- `GET /api/schedule-exceptions/{id}/` - Ver detalle de excepción
- `GET /api/schedule-exceptions/upcoming/` - Ver excepciones próximas (30 días)
- `POST /api/schedule-exceptions/` - Crear nueva excepción
```json
{
    "barber": 1,
    "date": "2024-03-25",
    "exception_type": "holiday",
    "description": "Día festivo",
    "is_active": true
}
```
- `PUT /api/schedule-exceptions/{id}/` - Actualizar excepción
- `DELETE /api/schedule-exceptions/{id}/` - Eliminar excepción

#### Gestión de Citas
- `GET /api/appointments/` - Listar citas (filtradas según el rol del usuario)
- `GET /api/appointments/{id}/` - Ver detalle de cita
- `GET /api/appointments/upcoming/` - Ver próximas citas (30 días)
- `GET /api/appointments/today/` - Ver citas del día
- `POST /api/appointments/` - Crear nueva cita
```json
{
    "barber": 1,
    "service": 1,
    "date": "2024-03-20",
    "start_time": "10:00:00",
    "notes": "Notas adicionales"
}
```
- `PATCH /api/appointments/{id}/change_status/` - Cambiar estado de cita
```json
{
    "status": "confirmed"  // pending, confirmed, cancelled, completed
}
```
- `DELETE /api/appointments/{id}/` - Cancelar cita (solo admin o cliente si está pendiente)

### Reglas de Negocio

#### Citas
1. **Creación de Citas**
   - No se pueden crear citas para fechas pasadas
   - El barbero debe tener horario disponible para ese día
   - La hora debe estar dentro del horario del barbero
   - No debe haber superposición con otras citas
   - No debe haber excepciones para esa fecha/hora

2. **Estados de Citas**
   - Transiciones permitidas:
     * pending → confirmed, cancelled
     * confirmed → completed, cancelled
     * cancelled → (estado final)
     * completed → (estado final)

3. **Permisos**
   - Clientes: ver y crear citas, cancelar sus citas pendientes
   - Barberos: ver sus citas, actualizar estados
   - Administradores: acceso completo

#### Horarios
1. **Configuración**
   - Intervalos mínimos de 15 minutos
   - Intervalos máximos de 120 minutos
   - Periodo de descanso opcional
   - No superposición de horarios por barbero

2. **Excepciones**
   - Días festivos
   - Vacaciones
   - Ausencias personales
   - No se pueden crear excepciones para fechas pasadas

### Roles y Permisos

1. **Admin**
   - Acceso total a todas las operaciones
   - Puede crear, modificar y eliminar barberos
   - Gestión completa de horarios

2. **Barbero**
   - Ver su propio perfil y horarios
   - Gestionar sus horarios
   - Ver lista de citas

3. **Cliente**
   - Ver lista de barberos y horarios
   - Ver perfil de barberos
   - Agendar citas

