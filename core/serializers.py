from rest_framework import serializers
from .models import Doctor, Patient, Appointment
from datetime import datetime, timedelta
from django.utils import timezone

class DoctorSerializer(serializers.ModelSerializer):
    available_slots = serializers.SerializerMethodField()
    
    def get_available_slots(self, obj):
        date_str = self.context.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        slots=[]
        current = timezone.make_aware(datetime.combine(date, obj.work_start))
        end = timezone.make_aware(datetime.combine(date, obj.work_end))

        while current < end:
            slots.append(current)
            current += timedelta(minutes=30)

        booked = Appointment.objects.filter(
            doctor = obj,
            slot_time__date = date,
            status = 'booked'
        ).values_list('slot_time', flat=True)

        available = [slot for slot in slots if slot not in booked]
        return[slot.strftime('%Y-%m-%d %H:%M') for slot in available]
    class Meta:
        model = Doctor
        fields = ['id', 'full_name', 'email', 'work_start', 'work_end', 'available_slots']

class PatientSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Patient
        fields = ['id', 'full_name', 'email', 'phone_number']

class AppointmentSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = Appointment
        fields=['id', 'doctor', 'patient', 'slot_time', 'status', 'cancel_reason', 'created_at', 'updated_at']
