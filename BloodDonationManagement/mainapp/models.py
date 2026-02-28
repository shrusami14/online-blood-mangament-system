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
        ('Paid', 'Paid'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled')
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


class Certificate(models.Model):
    """
    Model representing a digital certificate for blood donation.
    Generated when a donor's status is approved.
    """
    # Unique certificate ID (e.g., CERT-2024-0001)
    certificate_id = models.CharField(max_length=50, unique=True)
    
    # Link to the donor
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='certificates')
    
    # Certificate details
    donor_name = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=5)
    date_of_donation = models.DateField()
    issued_at = models.DateTimeField(auto_now_add=True)
    
    # Certificate message
    message = models.CharField(max_length=200, default="Thank you for saving lives")
    
    def __str__(self):
        return f"Certificate {self.certificate_id} - {self.donor_name}"

    class Meta:
        ordering = ['-issued_at']


class Payment(models.Model):
    """
    Model representing a payment transaction for blood requests.
    This is a demo/simulated payment system using Paytm.
    """
    # Payment choices
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
        ('Cancelled', 'Cancelled')
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('Paytm', 'Paytm'),
        ('Card', 'Card'),
        ('UPI', 'UPI'),
        ('Net Banking', 'Net Banking')
    ]

    # Link to blood request
    blood_request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    payment_id = models.CharField(max_length=50, unique=True)  # Random generated payment ID
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='Paytm')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # Timestamps
    payment_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional info
    transaction_id = models.CharField(max_length=100, blank=True, null=True)  # Paytm transaction ID
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.status} - ₹{self.amount}"
    
    class Meta:
        ordering = ['-payment_date']
