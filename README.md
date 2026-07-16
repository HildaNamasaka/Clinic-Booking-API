# Clinic Booking System — Savannah Informatics Backend Assessment

## Overview
A REST API for a small clinic booking system built with Django REST Framework. Patients can view available slots, book appointments, cancel, and reschedule. Doctors have set working hours and work in 30-minute slots.


## Step 1: Use Cases & Constraints

### Use Cases
- A patient can view all available 30-minute slots for a doctor on a given date
- A patient can book an available slot
- A patient can cancel a booking with a reason
- A patient can reschedule a booking to a new slot with the same doctor
- A patient can view their upcoming appointments sorted by date

### Out of Scope
- User authentication and authorization
- Payment processing
- Email/SMS notifications
- Switching doctors during rescheduling

### Constraints & Assumptions
- Slots are fixed at 30-minute intervals
- A doctor can have a maximum of 16 slots per 8-hour working day
- A booking cannot be made in the past or within 1 hour of the current time
- A slot must fall within the doctor's working hours
- A cancelled appointment cannot be rescheduled
- A patient can only reschedule with the same doctor
- All datetimes are stored in UTC

## Step 2: High Level Design---
Client
│

Django REST Framework API
│
|- GET  /api/doctors/{id}/availability
|- POST /api/appointments/
|- PATCH /api/appointments/{id}/cancel/
|-PATCH /api/appointments/{id}/reschedule/
|- GET  /api/patients/{id}/appointments/
│
PostgreSQL Database (Render)


## Step 3: Core Models

### Doctor
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| full_name | CharField | Doctor's full name |
| email | EmailField | Unique |
| work_start | TimeField | e.g. 08:00 |
| work_end | TimeField | e.g. 17:00 |

### Patient
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| full_name | CharField | Patient's full name |
| email | EmailField | Unique |
| phone_number | CharField | e.g. +254712345678 |

### Appointment
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| doctor | ForeignKey | FK to Doctor |
| patient | ForeignKey | FK to Patient |
| slot_time | DateTimeField | Stored in UTC |
| status | CharField | booked or cancelled |
| cancel_reason | TextField | Nullable |
| created_at | DateTimeField | Auto timestamp |
| updated_at | DateTimeField | Auto timestamp |



## Step 4: Key Decisions & Trade-offs

### Slot Generation
Slots are generated dynamically from the doctor's work_start and work_end in 30-minute intervals. They are not stored in the database, keeping the schema simple and avoiding stale or orphaned slot records. Trade-off: at scale, dynamic generation could become slow and may need caching.

### Concurrency — Preventing Double Booking
Booking uses select_for_update() inside transaction.atomic(). This locks the relevant rows during the check-and-insert operation, preventing two simultaneous requests from both passing the availability check and creating a duplicate booking. This is a classic race condition that a unique constraint alone cannot prevent under concurrent load.

### Timezone
All datetimes are stored as UTC using Django's USE_TZ = True setting. make_aware() is used during slot generation to ensure generated slots are timezone-aware and comparable to UTC-stored appointment times in the database.

### Slot Availability After Cancellation
When an appointment is cancelled, the slot automatically becomes available again because availability is calculated dynamically — the query filters only appointments with status='booked'. No manual slot freeing is needed.

### Database
PostgreSQL in production (Render), SQLite for local development via dj-database-url and the DATABASE_URL environment variable.

### Authentication
Not implemented in this version — noted as a required addition before production deployment. In production, JWT-based authentication would control who can book on behalf of whom.



## Step 5: API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/doctors/{id}/availability/?date=YYYY-MM-DD | List available 30-min slots |
| POST | /api/appointments/ | Book a slot |
| PATCH | /api/appointments/{id}/cancel/ | Cancel with reason |
| PATCH | /api/appointments/{id}/reschedule/ | Move to new slot |
| GET | /api/patients/{id}/appointments/ | Upcoming appointments sorted by date |



## How to Run Locally


git clone https://github.com/HildaNamasaka/Clinic-Booking-API.git
cd Clinic-Booking-API
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver




## Deployment
- **Platform:** Render.com
- **Live URL:** https://clinic-booking-api-0bx3.onrender.com
- **Branch that triggers deployment:** main
- **How:** Merging to main triggers the GitHub Actions pipeline which runs tests then calls the Render deploy hook to auto-deploy



## CI/CD
GitHub Actions pipeline (.github/workflows/deploy.yml):
- Runs the full test suite on every push and pull request to main
- Blocks deployment if any test fails
- Automatically deploys to Render on merge to main via deploy hook


## Section 4: AI Reflection

**1. What did you use AI for across the four sections?**
- Section 1: Used AI to help structure the README and identify trade-offs worth documenting such as dynamic slot generation vs storing slots in the DB
- Section 2: Used AI to debug the slot generation logic in the serializer, suggest select_for_update() for concurrency control, and review view logic for edge cases
- Section 3: Used AI to generate the GitHub Actions YAML structure and configure the Render deploy hook integration

**2. Give one example where an AI suggestion improved your work. What did you prompt it with?**
 I prompted AI with "how do I prevent two patients from booking the same slot at the same time?" — it suggested using 
 select_for_update() inside transaction.atomic(). This was a significant improvement because a simple filter check without 
 locking would have allowed race conditions under concurrent load. The suggestion made the booking logic production-grade 
 rather than just functionally correct.

**3. Give one example where AI output was wrong or incomplete and how you caught it.**
 AI provided the get_available_slots serializer logic using datetime.combine(date, obj.work_start) without accounting for the 
 fact that date arrives as a raw string from request.query_params. When I tested the availability endpoint I got TypeError: 
 combine() argument 1 must be datetime.date, not str. I caught it by reading the error traceback carefully and fixed it by 
 parsing the string first using datetime.strptime(date_str, '%Y-%m-%d').date() before passing it to combine().

**4. Name two decisions you made without AI. Why did you trust your own judgment there?**
 - I moved the available_slots logic from AppointmentSerializer to DoctorSerializer. AI initially suggested it in 
 AppointmentSerializer but I caught that Appointment has no work_start or work_end fields — availability is a property of a 
 Doctor, not an Appointment. I trusted my own judgment because I could see from the models that the logic was in the wrong 
 place.
 - I chose direct model manipulation for the cancel endpoint instead of using the serializer. Since I was only updating two 
 fields (status hardcoded, cancel_reason from request) and one of them was not coming from the user, mixing them through a 
 serializer felt unnecessarily complex. I made this call based on clarity and simplicity.
