from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Schedule, Service

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

    class Meta:
        model = Schedule
        fields = ('id', 'barber', 'barber_name', 'day_of_week', 'day_of_week_display',
                 'start_time', 'end_time', 'is_active')
        read_only_fields = ('barber_name', 'day_of_week_display')

    def validate(self, data):
        """
        Validar que:
        1. La hora de inicio sea anterior a la hora de fin
        2. No haya superposición de horarios para el mismo barbero
        """
        if data.get('start_time') and data.get('end_time'):
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError(
                    "La hora de inicio debe ser anterior a la hora de fin"
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