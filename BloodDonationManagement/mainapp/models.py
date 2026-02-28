from django.db import models
from django.contrib.auth.models import User


class Donor(models.Model):
    """Model representing a blood donor"""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ])
    blood_group = models.CharField(max_length=5, choices=[
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ])
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    last_donation = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.blood_group} ({self.status})"

    class Meta:
        ordering = ['-created_at']


class BloodRequest(models.Model):
    """Model representing a blood request"""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ]
    
    URGENCY_CHOICES = [
        ('Normal', 'Normal'),
        ('Urgent', 'Urgent'),
        ('Critical', 'Critical')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=5, choices=[
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ])
    units = models.IntegerField(default=1)
    hospital = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='Normal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient_name} - {self.blood_group} ({self.status})"

    class Meta:
        ordering = ['-created_at']


class BloodStock(models.Model):
    """Model representing blood stock inventory"""
    blood_group = models.CharField(max_length=5, unique=True, choices=[
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ])
    units_available = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.blood_group}: {self.units_available} units"

    class Meta:
        ordering = ['blood_group']
