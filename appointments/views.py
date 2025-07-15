from rest_framework import status, generics, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .serializers import (
    UserSerializer, CustomTokenObtainPairSerializer,
    BarberSerializer, ScheduleSerializer
)
from .models import Schedule

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
