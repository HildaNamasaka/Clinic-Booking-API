from django.contrib import admin
from .models import Doctor, Patient, Appointment

# Register your models here.
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'work_start', 'work_end']

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display= ['full_name', 'email', 'phone_number']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'patient', 'slot_time', 'status', 'cancel_reason']