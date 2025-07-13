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
  - Django REST Framework
  - MySQL
  - JWT para autenticación

- **Frontend (En desarrollo):**
  - React
  - Material-UI (próximamente)

- **Herramientas:**
  - Docker (próximamente)
  - Git para control de versiones

## 📋 Prerrequisitos

- Python 3.13.3 o superior
- MySQL
- Pip (gestor de paquetes de Python)
- Entorno virtual de Python (venv)

## 🔧 Instalación

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

5. **Aplicar migraciones**
   ```bash
   python manage.py migrate
   ```

6. **Cargar datos iniciales**
   ```sql
   mysql -u tu_usuario -p barbershop_db < database_setup.sql
   ```

7. **Iniciar el servidor de desarrollo**
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
├── media/               # Archivos subidos por usuarios
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

## 🔜 Próximas Características

- [ ] Integración con React
- [ ] Implementación de Docker
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
* etc. 