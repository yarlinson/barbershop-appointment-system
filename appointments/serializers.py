from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Schedule

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