from django.contrib import admin
from .models import Donor, BloodRequest


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ['name', 'blood_group', 'city', 'phone', 'created_at']
    search_fields = ['name', 'city', 'blood_group']
    list_filter = ['blood_group', 'gender', 'city']


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'blood_group', 'units', 'hospital', 'city', 'status', 'urgency', 'created_at']
    search_fields = ['patient_name', 'hospital', 'city', 'blood_group']
    list_filter = ['status', 'urgency', 'blood_group', 'city']
