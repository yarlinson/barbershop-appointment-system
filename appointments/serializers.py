from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Schedule, Service, ScheduleException, Appointment
from datetime import datetime, timedelta

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name',
                 'role', 'phone_number', 'address', 'profile_picture', 'is_active')
        read_only_fields = ('is_active',)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data

class ScheduleSerializer(serializers.ModelSerializer):
    barber_name = serializers.CharField(source='barber.get_full_name', read_only=True)
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    available_slots = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = (
            'id', 'barber', 'barber_name', 'day_of_week', 'day_of_week_display',
            'start_time', 'end_time', 'is_active', 'interval_minutes',
            'break_start_time', 'break_end_time', 'available_slots'
        )
        read_only_fields = ('barber_name', 'day_of_week_display', 'available_slots')

    def get_available_slots(self, obj):
        """
        Obtiene los slots disponibles para la fecha especificada
        """
        date_param = self.context.get('request').query_params.get('date')
        if not date_param:
            return None
        
        try:
            date = datetime.strptime(date_param, '%Y-%m-%d').date()
            duration_param = self.context.get('request').query_params.get('duration', '30')
            duration = timedelta(minutes=int(duration_param))
            
            slots = obj.get_available_slots(date, duration)
            return [slot.strftime('%H:%M') for slot in slots]
        except (ValueError, TypeError):
            return None

    def validate(self, data):
        """
        Validar que:
        1. La hora de inicio sea anterior a la hora de fin
        2. No haya superposición de horarios para el mismo barbero
        3. El intervalo sea válido
        4. El periodo de descanso sea válido si se especifica
        """
        # Validar hora inicio < hora fin
        if data.get('start_time') and data.get('end_time'):
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError(
                    "La hora de inicio debe ser anterior a la hora de fin"
                )

        # Validar intervalo
        if data.get('interval_minutes'):
            if data['interval_minutes'] < 15:
                raise serializers.ValidationError(
                    "El intervalo mínimo entre citas debe ser de 15 minutos"
                )
            if data['interval_minutes'] > 120:
                raise serializers.ValidationError(
                    "El intervalo máximo entre citas debe ser de 120 minutos"
                )

        # Validar periodo de descanso
        if data.get('break_start_time') and data.get('break_end_time'):
            if data['break_start_time'] >= data['break_end_time']:
                raise serializers.ValidationError(
                    "La hora de inicio del descanso debe ser anterior a la hora de fin"
                )
            if data.get('start_time') and data.get('end_time'):
                if (data['break_start_time'] < data['start_time'] or
                    data['break_end_time'] > data['end_time']):
                    raise serializers.ValidationError(
                        "El periodo de descanso debe estar dentro del horario laboral"
                    )

        # Validar superposición solo si tenemos todos los datos necesarios
        if self.instance is None and all(key in data for key in ['barber', 'day_of_week', 'start_time', 'end_time']):
            overlapping = Schedule.objects.filter(
                barber=data['barber'],
                day_of_week=data['day_of_week'],
                is_active=True
            ).exclude(
                id=self.instance.id if self.instance else None
            ).filter(
                start_time__lt=data['end_time'],
                end_time__gt=data['start_time']
            ).exists()

            if overlapping:
                raise serializers.ValidationError(
                    "Este horario se superpone con otro horario existente del barbero"
                )

        return data

class ScheduleExceptionSerializer(serializers.ModelSerializer):
    barber_name = serializers.CharField(source='barber.get_full_name', read_only=True)
    exception_type_display = serializers.CharField(source='get_exception_type_display', read_only=True)

    class Meta:
        model = ScheduleException
        fields = (
            'id', 'barber', 'barber_name', 'date', 'start_time', 'end_time',
            'exception_type', 'exception_type_display', 'description',
            'is_active', 'created_at', 'updated_at'
        )
        read_only_fields = ('barber_name', 'exception_type_display', 'created_at', 'updated_at')

    def validate(self, data):
        """
        Validar que:
        1. La fecha no sea en el pasado
        2. Si se especifican horas, inicio sea anterior a fin
        3. No haya superposición con otras excepciones
        """
        # Validar fecha
        if data.get('date'):
            if data['date'] < datetime.now().date():
                raise serializers.ValidationError(
                    "No se pueden crear excepciones para fechas pasadas"
                )

        # Validar horas si se especifican ambas
        if data.get('start_time') and data.get('end_time'):
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError(
                    "La hora de inicio debe ser anterior a la hora de fin"
                )

        # Validar superposición
        if self.instance is None and all(key in data for key in ['barber', 'date']):
            overlapping = ScheduleException.objects.filter(
                barber=data['barber'],
                date=data['date'],
                is_active=True
            ).exists()

            if overlapping:
                raise serializers.ValidationError(
                    "Ya existe una excepción para esta fecha y barbero"
                )

        return data

class BarberSerializer(serializers.ModelSerializer):
    schedules = ScheduleSerializer(many=True, read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'full_name',
                 'phone_number', 'address', 'profile_picture', 'is_active', 'schedules')
        read_only_fields = ('is_active', 'full_name', 'schedules')

    def validate(self, data):
        if self.instance and self.instance.role != 'barber':
            raise serializers.ValidationError("Este usuario no es un barbero")
        return data

class ServiceSerializer(serializers.ModelSerializer):
    duration_display = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = (
            'id', 'name', 'description', 'price', 'duration',
            'duration_display', 'image', 'is_active',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')

    def get_duration_display(self, obj):
        """
        Convierte la duración a un formato más legible
        """
        minutes = obj.duration.total_seconds() / 60
        hours = int(minutes // 60)
        remaining_minutes = int(minutes % 60)
        
        if hours > 0 and remaining_minutes > 0:
            return f"{hours}h {remaining_minutes}min"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{remaining_minutes}min"

    def validate_price(self, value):
        """
        Validar que el precio sea positivo
        """
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor que 0")
        return value

    def validate_duration(self, value):
        """
        Validar que la duración sea positiva y no exceda las 4 horas
        """
        minutes = value.total_seconds() / 60
        if minutes <= 0:
            raise serializers.ValidationError("La duración debe ser positiva")
        if minutes > 240:  # 4 horas
            raise serializers.ValidationError("La duración no puede exceder las 4 horas")
        return value 

class AppointmentSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    barber_name = serializers.CharField(source='barber.get_full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_duration = serializers.DurationField(source='service.duration', read_only=True)
    service_price = serializers.DecimalField(source='service.price', read_only=True, max_digits=10, decimal_places=2)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Appointment
        fields = (
            'id', 'client', 'client_name', 'barber', 'barber_name',
            'service', 'service_name', 'service_duration', 'service_price',
            'date', 'start_time', 'end_time', 'status', 'status_display',
            'notes', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'client_name', 'barber_name', 'service_name',
            'service_duration', 'service_price', 'status_display',
            'end_time', 'created_at', 'updated_at'
        )

    def validate(self, data):
        """
        Validar que:
        1. La fecha no sea en el pasado
        2. El barbero tenga horario para ese día
        3. El horario esté dentro del horario del barbero
        4. No haya superposición con otras citas
        5. No haya excepciones para esa fecha
        """
        if not self.instance:  # Solo para nuevas citas
            # Validar fecha
            if data['date'] < datetime.now().date():
                raise serializers.ValidationError(
                    "No se pueden crear citas para fechas pasadas"
                )

            # Obtener el día de la semana (0 = Lunes, 6 = Domingo)
            day_of_week = data['date'].weekday()

            # Verificar si el barbero tiene horario para ese día
            schedule = Schedule.objects.filter(
                barber=data['barber'],
                day_of_week=day_of_week,
                is_active=True
            ).first()

            if not schedule:
                raise serializers.ValidationError(
                    f"El barbero no tiene horario para el día {data['date']}"
                )

            # Verificar si hay excepciones para esa fecha
            exception_exists = ScheduleException.objects.filter(
                barber=data['barber'],
                date=data['date'],
                is_active=True
            ).exists()

            if exception_exists:
                raise serializers.ValidationError(
                    "El barbero no está disponible en esta fecha"
                )

            # Verificar que la hora esté dentro del horario del barbero
            if (data['start_time'] < schedule.start_time or
                data['start_time'] >= schedule.end_time):
                raise serializers.ValidationError(
                    "La hora de la cita está fuera del horario del barbero"
                )

            # Verificar si está en periodo de descanso
            if schedule.break_start_time and schedule.break_end_time:
                if (data['start_time'] >= schedule.break_start_time and
                    data['start_time'] < schedule.break_end_time):
                    raise serializers.ValidationError(
                        "La hora de la cita está en el periodo de descanso del barbero"
                    )

            # Calcular hora de fin basada en la duración del servicio
            service_duration = data['service'].duration
            end_time = (
                datetime.combine(datetime.min, data['start_time']) +
                service_duration
            ).time()

            # Verificar que la cita no se extienda más allá del horario
            if end_time > schedule.end_time:
                raise serializers.ValidationError(
                    "La duración del servicio excede el horario del barbero"
                )

            # Verificar superposición con otras citas
            overlapping = Appointment.objects.filter(
                barber=data['barber'],
                date=data['date'],
                status__in=['pending', 'confirmed'],
            ).filter(
                start_time__lt=end_time,
                end_time__gt=data['start_time']
            ).exists()

            if overlapping:
                raise serializers.ValidationError(
                    "Ya existe una cita en este horario"
                )

            # Guardar la hora de fin calculada
            self.context['end_time'] = end_time

        return data

    def create(self, validated_data):
        """
        Crear una cita asignando automáticamente:
        1. El cliente (usuario actual)
        2. La hora de fin (basada en la duración del servicio)
        3. El estado inicial (pending)
        """
        validated_data['client'] = self.context['request'].user
        validated_data['end_time'] = self.context['end_time']
        validated_data['status'] = 'pending'
        return super().create(validated_data) 