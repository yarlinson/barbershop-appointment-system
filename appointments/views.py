from rest_framework import status, generics, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
from .serializers import (
    UserSerializer, CustomTokenObtainPairSerializer,
    BarberSerializer, ScheduleSerializer, ServiceSerializer,
    ScheduleExceptionSerializer, AppointmentSerializer
)
from .models import Schedule, Service, ScheduleException, Appointment

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BarberViewSet(viewsets.ModelViewSet):
    """
    ViewSet para la gestión de barberos.
    Proporciona operaciones CRUD y endpoints adicionales para gestión de horarios.
    """
    queryset = User.objects.filter(role='barber')
    serializer_class = BarberSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Asegurar que los nuevos usuarios creados aquí sean barberos
        """
        serializer.save(role='barber')

    def get_permissions(self):
        """
        Asignar permisos según la acción:
        - Lista y detalle: cualquier usuario autenticado
        - Crear, actualizar, eliminar: solo administradores
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    @action(detail=True, methods=['get', 'post'])
    def schedules(self, request, pk=None):
        """
        GET: Obtener los horarios de un barbero específico
        POST: Agregar un nuevo horario para el barbero
        """
        barber = self.get_object()
        
        if request.method == 'GET':
            schedules = Schedule.objects.filter(barber=barber)
            serializer = ScheduleSerializer(schedules, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = ScheduleSerializer(data={**request.data, 'barber': barber.id})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put', 'delete'])
    def schedule(self, request, pk=None):
        """
        PUT: Actualizar un horario existente del barbero
        DELETE: Eliminar un horario del barbero
        """
        barber = self.get_object()
        schedule_id = request.data.get('schedule_id') or request.query_params.get('schedule_id')
        
        if not schedule_id:
            return Response(
                {"detail": "Se requiere el ID del horario"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        schedule = get_object_or_404(Schedule, id=schedule_id, barber=barber)
        
        if request.method == 'PUT':
            serializer = ScheduleSerializer(schedule, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        elif request.method == 'DELETE':
            schedule.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para la gestión de servicios.
    Proporciona operaciones CRUD para los servicios de la barbería.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtrar servicios activos para usuarios normales,
        mostrar todos los servicios para administradores
        """
        if self.request.user.is_staff:
            return Service.objects.all()
        return Service.objects.filter(is_active=True)

    def get_permissions(self):
        """
        Asignar permisos según la acción:
        - Lista y detalle: cualquier usuario autenticado
        - Crear, actualizar, eliminar: solo administradores
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        """
        Activar/desactivar un servicio
        """
        service = self.get_object()
        service.is_active = not service.is_active
        service.save()
        serializer = self.get_serializer(service)
        return Response(serializer.data)

class ScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet para la gestión de horarios.
    """
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtrar horarios:
        - Administradores ven todos los horarios
        - Barberos ven solo sus horarios
        - Clientes ven solo horarios activos
        """
        queryset = Schedule.objects.all()
        
        if self.request.user.is_staff:
            return queryset
        elif self.request.user.role == 'barber':
            return queryset.filter(barber=self.request.user)
        else:
            return queryset.filter(is_active=True)

    def get_permissions(self):
        """
        - Lista y detalle: cualquier usuario autenticado
        - Crear, actualizar, eliminar: solo administradores y barberos para sus propios horarios
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        Si el usuario es un barbero, asignar el horario a sí mismo
        """
        if self.request.user.role == 'barber':
            serializer.save(barber=self.request.user)
        else:
            serializer.save()

    def check_object_permissions(self, request, obj):
        """
        Verificar que los barberos solo puedan modificar sus propios horarios
        """
        super().check_object_permissions(request, obj)
        if request.user.role == 'barber' and obj.barber != request.user:
            self.permission_denied(
                request,
                message="No tienes permiso para modificar los horarios de otros barberos"
            )

class ScheduleExceptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para la gestión de excepciones de horarios.
    """
    serializer_class = ScheduleExceptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtrar excepciones:
        - Administradores ven todas las excepciones
        - Barberos ven solo sus excepciones
        - Clientes ven solo excepciones activas y futuras
        """
        queryset = ScheduleException.objects.all()
        
        if self.request.user.is_staff:
            return queryset
        elif self.request.user.role == 'barber':
            return queryset.filter(barber=self.request.user)
        else:
            return queryset.filter(
                is_active=True,
                date__gte=timezone.now().date()
            )

    def get_permissions(self):
        """
        - Lista y detalle: cualquier usuario autenticado
        - Crear, actualizar, eliminar: solo administradores y barberos para sus propias excepciones
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        Si el usuario es un barbero, asignar la excepción a sí mismo
        """
        if self.request.user.role == 'barber':
            serializer.save(barber=self.request.user)
        else:
            serializer.save()

    def check_object_permissions(self, request, obj):
        """
        Verificar que los barberos solo puedan modificar sus propias excepciones
        """
        super().check_object_permissions(request, obj)
        if request.user.role == 'barber' and obj.barber != request.user:
            self.permission_denied(
                request,
                message="No tienes permiso para modificar las excepciones de otros barberos"
            )

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Obtener excepciones próximas (próximos 30 días)
        """
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)
        
        exceptions = self.get_queryset().filter(
            date__range=[start_date, end_date],
            is_active=True
        )
        
        serializer = self.get_serializer(exceptions, many=True)
        return Response(serializer.data)

class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para la gestión de citas.
    """
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtrar citas según el rol del usuario:
        - Administradores ven todas las citas
        - Barberos ven sus citas
        - Clientes ven sus propias citas
        """
        queryset = Appointment.objects.all()
        
        if self.request.user.is_staff:
            return queryset
        elif self.request.user.role == 'barber':
            return queryset.filter(barber=self.request.user)
        else:
            return queryset.filter(client=self.request.user)

    def get_permissions(self):
        """
        - Crear: cualquier usuario autenticado
        - Ver detalle: cliente de la cita, barbero asignado o admin
        - Actualizar estado: barbero asignado o admin
        - Eliminar: admin o cliente (si está pendiente)
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def check_object_permissions(self, request, obj):
        """
        Verificar permisos específicos para cada acción
        """
        super().check_object_permissions(request, obj)
        
        # Solo el cliente, el barbero asignado o admin pueden ver el detalle
        if self.action == 'retrieve':
            if not (request.user.is_staff or 
                   request.user == obj.client or 
                   request.user == obj.barber):
                self.permission_denied(request, message="No tienes permiso para ver esta cita")
        
        # Solo el barbero asignado o admin pueden actualizar el estado
        elif self.action in ['update', 'partial_update']:
            if not (request.user.is_staff or request.user == obj.barber):
                self.permission_denied(request, message="No tienes permiso para actualizar esta cita")
        
        # Solo el admin o el cliente pueden cancelar (si está pendiente)
        elif self.action == 'destroy':
            if not (request.user.is_staff or 
                   (request.user == obj.client and obj.status == 'pending')):
                self.permission_denied(request, message="No tienes permiso para cancelar esta cita")

    @action(detail=True, methods=['patch'])
    def change_status(self, request, pk=None):
        """
        Cambiar el estado de una cita
        """
        appointment = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Appointment.STATUS_CHOICES):
            return Response(
                {"detail": "Estado no válido"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Validar transiciones de estado permitidas
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['completed', 'cancelled'],
            'cancelled': [],
            'completed': []
        }
        
        if new_status not in valid_transitions[appointment.status]:
            return Response(
                {"detail": f"No se puede cambiar de {appointment.status} a {new_status}"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        appointment.status = new_status
        appointment.save()
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Obtener las próximas citas (próximos 30 días)
        """
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)
        
        appointments = self.get_queryset().filter(
            date__range=[start_date, end_date],
            status__in=['pending', 'confirmed']
        )
        
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def today(self, request):
        """
        Obtener las citas del día
        """
        today = timezone.now().date()
        
        appointments = self.get_queryset().filter(
            date=today,
            status__in=['pending', 'confirmed']
        )
        
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)
