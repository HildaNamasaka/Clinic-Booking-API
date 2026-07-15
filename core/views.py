from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.views import APIView
from .serializers import AppointmentSerializer, DoctorSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Doctor, Patient, Appointment
from datetime import datetime


# Create your views here.
class BookAppointment(APIView):
    def post(self, request):
        doctor = Doctor.objects.get(id=request.data.get('doctor'))
        slot_time = datetime.strptime(request.data.get('slot_time'), '%Y-%m-%d %H:%M')
        
        if slot_time.time() < doctor.work_start or slot_time.time() > doctor.work_end:
            return Response({'Error' : 'Slot is outside working hours'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            already_booked = Appointment.objects.select_for_update().filter(
                doctor=doctor,
                slot_time = slot_time,
                status='booked'
            ).exists()
            if already_booked:
                return Response({'Error' : 'Slot already booked'}, status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = AppointmentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message' :'Slot booked successfully', 'data' : serializer.data}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AvailableSlots(APIView):
    def get_object(self, pk):
        return get_object_or_404(Doctor, id=pk)
    
    def get(self, request, pk):
        doctor = self.get_object(pk)
        date = request.query_params.get('date')
        serializer = DoctorSerializer(doctor, context={'date' : date})
        return Response(serializer.data, status=status.HTTP_200_OK)

class CancelAppointment(APIView):
    def get_object(self, pk):
        return get_object_or_404(Appointment, id=pk)
    
    def patch(self, request, pk):
        appointment = self.get_object(pk)
        
        if appointment.status == Appointment.Status.CANCELLED:
            return Response({'Error' : 'Appointment already cancelled'}, status=status.HTTP_400_BAD_REQUEST)
        appointment.status = Appointment.Status.CANCELLED
        appointment.cancel_reason = request.data.get('cancel_reason')
        appointment.save()
        
        return Response({'Message' : 'Appointment cancelled suuccessfully'}, status=status.HTTP_200_OK)

class RescheduleAppointment(APIView):
    def get_object(self, pk):
        return get_object_or_404(Appointment, id=pk)
    
    def patch(self, request, pk):
        appointment = self.get_object(pk)

        if appointment.status == Appointment.Status.CANCELLED:
            return Response({'Error' : 'You cannot reschedule a cancelled appointment'}, status=status.HTTP_400_BAD_REQUEST)
        new_slot_time = datetime.strptime(request.data.get('slot_time'),'%Y-%m-%d %H:%M')

        if new_slot_time.time() < appointment.doctor.work_start or new_slot_time.time() > appointment.doctor.work_end:
            return Response({'Error' : 'Slot outside working houres'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            already_booked = Appointment.objects.select_for_update().filter(
                doctor = appointment.doctor,
                slot_time = new_slot_time,
                status = 'booked'
            ).exists()
            if already_booked:
                return Response({'Error' : 'The slot is already booked.'}, status=status.HTTP_400_BAD_REQUEST)
            appointment.slot_time = new_slot_time
            appointment.save()

            return Response({'Message' : 'Appointment rescheduled successfully'}, status=status.HTTP_200_OK)

class UpcomingAppointments(APIView):
    def get_object(self, pk):
        return get_object_or_404(Patient, id=pk)
    
    def get(self, request, pk):
        patient = self.get_object(pk)
        appointments = Appointment.objects.filter(
            patient=patient,
            status = 'booked',
            slot_time__gte=datetime.now()
        ).order_by('slot_time')
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)