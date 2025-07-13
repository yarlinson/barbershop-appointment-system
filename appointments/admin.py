from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Service, Schedule, Appointment

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Información Personal'), {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'address', 'profile_picture')}),
        (_('Permisos'), {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        (_('Información del Servicio'), {
            'fields': ('name', 'description', 'price', 'duration', 'image')
        }),
        (_('Estado'), {
            'fields': ('is_active',)
        }),
    )

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('barber', 'day_of_week', 'start_time', 'end_time', 'is_active')
    list_filter = ('day_of_week', 'is_active', 'barber')
    search_fields = ('barber__username', 'barber__first_name', 'barber__last_name')
    ordering = ('barber', 'day_of_week')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('barber')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'barber', 'service', 'date', 'start_time', 'status')
    list_filter = ('status', 'date', 'barber')
    search_fields = (
        'client__username', 'client__first_name', 'client__last_name',
        'barber__username', 'barber__first_name', 'barber__last_name'
    )
    ordering = ('-date', '-start_time')
    
    fieldsets = (
        (_('Información de la Cita'), {
            'fields': ('client', 'barber', 'service', 'date', 'start_time', 'end_time')
        }),
        (_('Estado y Notas'), {
            'fields': ('status', 'notes')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('client', 'barber', 'service')
