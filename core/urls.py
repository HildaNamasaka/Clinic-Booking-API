from django.urls import path
from .views import BookAppointment, AvailableSlots, CancelAppointment, RescheduleAppointment, UpcomingAppointments

urlpatterns = [
    path('appointments/', BookAppointment.as_view()),
    path('doctors/<int:pk>/availability/', AvailableSlots.as_view()),
    path('appointments/<int:pk>/cancel/', CancelAppointment.as_view()),
    path('appointments/<int:pk>/reschedule/', RescheduleAppointment.as_view()),
    path('patients/<int:pk>/appointments/', UpcomingAppointments.as_view()),
]