from rest_framework.test import APITestCase
from .models import Doctor, Patient, Appointment
from rest_framework import status
from datetime import datetime, timedelta

class BookAppointmentTestCase(APITestCase):
    def setUp(self):
        self.doctor = Doctor.objects.create(
            full_name='John Doe',
            email='jane@gmail.com',
            work_start='08:00',
            work_end='17:00'
        )
        self.patient = Patient.objects.create(
            full_name='Emily Brown',
            email='emily@gmail.com',
            phone_number='+254799999123'
        )
        future_date = datetime.now() + timedelta(days=5)
        clean_slot = future_date.replace(second=0, microsecond=0)
        self.appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            slot_time=clean_slot,
            status='booked'
        )

    def test_book_appointment_returns_201(self):
        data = {
            'doctor': self.doctor.id,
            'patient': self.patient.id,
            'slot_time': '2026-07-25 10:30'
        }
        response = self.client.post('/appointments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_book_past_slot_returns_400(self):
        data = {
            'doctor': self.doctor.id,
            'patient': self.patient.id,
            'slot_time': '2026-06-20 10:30'
        }
        response = self.client.post('/appointments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_book_slot_outside_working_hours_return_400(self):
        data = {
            'doctor': self.doctor.id,
            'patient': self.patient.id,
            'slot_time': '2026-07-25 18:30'
        }
        response = self.client.post('/appointments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_book_already_booked_slot_returns_400(self):
        data = {
            'doctor': self.doctor.id,
            'patient': self.patient.id,
            'slot_time': self.appointment.slot_time.strftime('%Y-%m-%d %H:%M')
        }
        response = self.client.post('/appointments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class CancelAppointmentTestCase(APITestCase):
    def setUp(self):
        self.doctor = Doctor.objects.create(
            full_name='John Doe',
            email='john@gmail.com',
            work_start='08:00',
            work_end='17:00'
        )
        self.patient = Patient.objects.create(
            full_name='Emily Brown',
            email='emily@gmail.com',
            phone_number='+254799999123'
        )
        future_date = datetime.now() + timedelta(days=5)
        clean_slot = future_date.replace(second=0, microsecond=0)
        self.appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            slot_time=clean_slot,
            status='booked'
        )

    def test_cancel_appointment_returns_200(self):
        response = self.client.patch(
            f'/appointments/{self.appointment.id}/cancel/',
            {'cancel_reason': 'Schedule conflict'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cancel_already_cancelled_returns_400(self):
        self.appointment.status = 'cancelled'
        self.appointment.save()
        response = self.client.patch(
            f'/appointments/{self.appointment.id}/cancel/',
            {'cancel_reason': 'Schedule conflict'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RescheduleAppointmentTestCase(APITestCase):
    def setUp(self):
        self.doctor = Doctor.objects.create(
            full_name='John Doe',
            email='john@gmail.com',
            work_start='08:00',
            work_end='17:00'
        )
        self.patient = Patient.objects.create(
            full_name='Emily Brown',
            email='emily@gmail.com',
            phone_number='+254799999123'
        )
        future_date = datetime.now() + timedelta(days=5)
        clean_slot = future_date.replace(second=0, microsecond=0)
        self.appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            slot_time=clean_slot,
            status='booked'
        )

    def test_reschedule_appointment_returns_200(self):
        new_slot = (datetime.now() + timedelta(days=6)).replace(second=0, microsecond=0)
        response = self.client.patch(
            f'/appointments/{self.appointment.id}/reschedule/',
            {'slot_time': new_slot.strftime('%Y-%m-%d %H:%M')},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reschedule_cancelled_appointment_returns_400(self):
        self.appointment.status = 'cancelled'
        self.appointment.save()
        new_slot = (datetime.now() + timedelta(days=6)).replace(second=0, microsecond=0)
        response = self.client.patch(
            f'/appointments/{self.appointment.id}/reschedule/',
            {'slot_time': new_slot.strftime('%Y-%m-%d %H:%M')},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)