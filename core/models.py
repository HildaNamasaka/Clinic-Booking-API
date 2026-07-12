from django.db import models

class Doctor(models.Model):
    full_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=250, unique=True)
    work_start = models.TimeField()
    work_end = models.TimeField()

    def __str__(self):
        return self.full_name
    
class Patient(models.Model):
    full_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=250, unique=True)
    phone_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.full_name

class Appointment(models.Model):
    class Status(models.TextChoices):
        BOOKED = 'booked', 'Booked'
        CANCELLED = 'cancelled', 'Cancelled'
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    slot_time = models.DateTimeField()
    status = models.CharField(max_length=250, choices=Status.choices, default=Status.BOOKED)
    cancel_reason = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('doctor', 'slot_time')
    
    def __str__(self):
        return f"{self.patient.full_name}'s appointment with {self.doctor.full_name}"