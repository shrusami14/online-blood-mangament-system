import os
import django
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodsystem.settings')
django.setup()

from django.contrib.auth.models import User
from mainapp.models import Donor, BloodRequest
from datetime import date

# Get or create a test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@example.com'}
)
if created:
    user.set_password('test123')
    user.save()
    print(f'Created test user: testuser / test123')
else:
    print(f'Using existing user: testuser')

# Create a test donor
donor, created = Donor.objects.get_or_create(
    name='John Doe',
    defaults={
        'user': user,
        'age': 30,
        'gender': 'Male',
        'blood_group': 'O+',
        'phone': '1234567890',
        'city': 'New York',
        'last_donation': date(2024, 1, 15)
    }
)
if created:
    print(f'Created donor: {donor.name}')
else:
    print(f'Donor already exists: {donor.name}')

# Create a test blood request
blood_request, created = BloodRequest.objects.get_or_create(
    patient_name='Jane Smith',
    defaults={
        'user': user,
        'blood_group': 'A+',
        'units': 2,
        'hospital': 'City Hospital',
        'city': 'Los Angeles',
        'urgency': 'Urgent',
        'status': 'Pending'
    }
)
if created:
    print(f'Created blood request for: {blood_request.patient_name}')
else:
    print(f'Blood request already exists for: {blood_request.patient_name}')

# Print all donors
print('\n--- All Donors in Database ---')
for d in Donor.objects.all():
    print(f'  {d.name} - {d.blood_group} - {d.city}')

# Print all blood requests
print('\n--- All Blood Requests in Database ---')
for r in BloodRequest.objects.all():
    print(f'  {r.patient_name} - {r.blood_group} - {r.status}')

print('\n--- Test data created successfully! ---')
print('Now you can view this data in the admin panel at http://127.0.0.1:8000/admin/')
