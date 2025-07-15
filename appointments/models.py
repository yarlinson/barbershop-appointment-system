from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from datetime import timedelta

class User(AbstractUser):
    """
    Modelo personalizado de Usuario que extiende del modelo base de Django
    """
    ROLE_CHOICES = (
        ('client', 'Cliente'),
        ('barber', 'Barbero'),
        ('admin', 'Administrador'),
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="El número debe estar en el formato: '+999999999'. Hasta 15 dígitos permitidos."
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    address = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('usuario')
        verbose_name_plural = _('usuarios')

    def __str__(self):
        return f"{self.get_full_name()} - {self.get_role_display()}"

class Service(models.Model):
    """
    Modelo para los servicios ofrecidos en la barbería
    """
    name = models.CharField(_('nombre'), max_length=100)
    description = models.TextField(_('descripción'))
    price = models.DecimalField(_('precio'), max_digits=10, decimal_places=2)
    duration = models.DurationField(_('duración'))
    image = models.ImageField(upload_to='services/', null=True, blank=True)
    is_active = models.BooleanField(_('activo'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('servicio')
        verbose_name_plural = _('servicios')

    def __str__(self):
        return f"{self.name} - ${self.price}"

class Schedule(models.Model):
    """
    Modelo para los horarios de los barberos
    """
    DAYS_OF_WEEK = (
        (0, _('Lunes')),
        (1, _('Martes')),
        (2, _('Miércoles')),
        (3, _('Jueves')),
        (4, _('Viernes')),
        (5, _('Sábado')),
        (6, _('Domingo')),
    )

    barber = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'barber'},
        related_name='schedules'
    )
    day_of_week = models.IntegerField(_('día de la semana'), choices=DAYS_OF_WEEK)
    start_time = models.TimeField(_('hora de inicio'))
    end_time = models.TimeField(_('hora de fin'))
    is_active = models.BooleanField(_('activo'), default=True)
    interval_minutes = models.IntegerField(
        _('intervalo en minutos'),
        default=30,
        help_text=_('Intervalo de tiempo entre citas en minutos')
    )
    break_start_time = models.TimeField(
        _('inicio del descanso'),
        null=True,
        blank=True,
        help_text=_('Hora de inicio del descanso (opcional)')
    )
    break_end_time = models.TimeField(
        _('fin del descanso'),
        null=True,
        blank=True,
        help_text=_('Hora de fin del descanso (opcional)')
    )

    class Meta:
        verbose_name = _('horario')
        verbose_name_plural = _('horarios')
        unique_together = ['barber', 'day_of_week']

    def __str__(self):
        return f"{self.barber.get_full_name()} - {self.get_day_of_week_display()}"

    def get_available_slots(self, date, duration=timedelta(minutes=30)):
        """
        Obtiene los slots disponibles para un día específico
        teniendo en cuenta las citas existentes y excepciones
        """
        from datetime import datetime, timedelta
        slots = []
        current_time = datetime.combine(date, self.start_time)
        end_datetime = datetime.combine(date, self.end_time)

        while current_time + duration <= end_datetime:
            # Verificar si el horario está en el periodo de descanso
            if self.break_start_time and self.break_end_time:
                break_start = datetime.combine(date, self.break_start_time)
                break_end = datetime.combine(date, self.break_end_time)
                if current_time >= break_start and current_time < break_end:
                    current_time = break_end
                    continue

            # Verificar si hay una excepción para esta fecha
            if ScheduleException.objects.filter(
                barber=self.barber,
                date=date,
                is_active=True
            ).exists():
                break

            # Verificar si hay citas que se superponen
            appointment_exists = Appointment.objects.filter(
                barber=self.barber,
                date=date,
                status__in=['pending', 'confirmed'],
                start_time__lt=(current_time + duration).time(),
                end_time__gt=current_time.time()
            ).exists()

            if not appointment_exists:
                slots.append(current_time.time())

            current_time += timedelta(minutes=self.interval_minutes)

        return slots

class ScheduleException(models.Model):
    """
    Modelo para manejar excepciones en los horarios (días festivos, vacaciones, etc.)
    """
    EXCEPTION_TYPES = (
        ('holiday', _('Día Festivo')),
        ('vacation', _('Vacaciones')),
        ('personal', _('Personal')),
        ('other', _('Otro')),
    )

    barber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'barber'},
        related_name='schedule_exceptions'
    )
    date = models.DateField(_('fecha'))
    start_time = models.TimeField(_('hora de inicio'), null=True, blank=True)
    end_time = models.TimeField(_('hora de fin'), null=True, blank=True)
    exception_type = models.CharField(
        _('tipo de excepción'),
        max_length=20,
        choices=EXCEPTION_TYPES,
        default='other'
    )
    description = models.TextField(_('descripción'), blank=True)
    is_active = models.BooleanField(_('activo'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('excepción de horario')
        verbose_name_plural = _('excepciones de horario')
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.barber.get_full_name()} - {self.get_exception_type_display()} - {self.date}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError(_('La hora de inicio debe ser anterior a la hora de fin'))

class Appointment(models.Model):
    """
    Modelo para las citas
    """
    STATUS_CHOICES = (
        ('pending', _('Pendiente')),
        ('confirmed', _('Confirmada')),
        ('cancelled', _('Cancelada')),
        ('completed', _('Completada')),
    )

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='client_appointments',
        limit_choices_to={'role': 'client'}
    )
    barber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='barber_appointments',
        limit_choices_to={'role': 'barber'}
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    date = models.DateField(_('fecha'))
    start_time = models.TimeField(_('hora de inicio'))
    end_time = models.TimeField(_('hora de fin'))
    status = models.CharField(
        _('estado'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    notes = models.TextField(_('notas'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('cita')
        verbose_name_plural = _('citas')
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f"Cita: {self.client.get_full_name()} con {self.barber.get_full_name()} - {self.date}"
