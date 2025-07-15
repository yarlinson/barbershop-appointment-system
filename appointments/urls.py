from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'appointments'

# Crear router para ViewSets
router = DefaultRouter()
router.register(r'barbers', views.BarberViewSet, basename='barber')
router.register(r'services', views.ServiceViewSet, basename='service')
router.register(r'schedules', views.ScheduleViewSet, basename='schedule')
router.register(r'schedule-exceptions', views.ScheduleExceptionViewSet, basename='schedule-exception')
router.register(r'appointments', views.AppointmentViewSet, basename='appointment')

urlpatterns = [
    # Autenticación
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    
    # Perfil de usuario
    path('auth/profile/', views.get_user_profile, name='user_profile'),
    path('auth/profile/update/', views.update_user_profile, name='update_profile'),

    # Incluir URLs del router
    path('', include(router.urls)),
] 