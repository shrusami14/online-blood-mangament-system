from django.contrib import admin
from .models import Donor, BloodRequest, BloodStock


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ['name', 'blood_group', 'city', 'phone', 'status', 'created_at']
    search_fields = ['name', 'city', 'blood_group', 'phone']
    list_filter = ['status', 'blood_group', 'gender', 'city']
    actions = ['approve_donors', 'reject_donors']

    def approve_donors(self, request, queryset):
        queryset.update(status='Approved')
        self.message_user(request, 'Selected donors have been approved.')

    def reject_donors(self, request, queryset):
        queryset.update(status='Rejected')
        self.message_user(request, 'Selected donors have been rejected.')

    approve_donors.short_description = "Approve selected donors"
    reject_donors.short_description = "Reject selected donors"


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'blood_group', 'units', 'hospital', 'city', 'status', 'urgency', 'created_at']
    search_fields = ['patient_name', 'hospital', 'city', 'blood_group']
    list_filter = ['status', 'urgency', 'blood_group', 'city']
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        for blood_request in queryset:
            if blood_request.status == 'Pending':
                # Reduce stock when approving
                try:
                    stock = BloodStock.objects.get(blood_group=blood_request.blood_group)
                    if stock.units_available >= blood_request.units:
                        stock.units_available -= blood_request.units
                        stock.save()
                        blood_request.status = 'Approved'
                        blood_request.save()
                    else:
                        self.message_user(request, f'Insufficient stock for {blood_request.blood_group}')
                except BloodStock.DoesNotExist:
                    blood_request.status = 'Approved'
                    blood_request.save()
        self.message_user(request, 'Selected requests have been approved.')

    def reject_requests(self, request, queryset):
        queryset.update(status='Rejected')
        self.message_user(request, 'Selected requests have been rejected.')

    approve_requests.short_description = "Approve selected blood requests (will deduct stock)"
    reject_requests.short_description = "Reject selected blood requests"


@admin.register(BloodStock)
class BloodStockAdmin(admin.ModelAdmin):
    list_display = ['blood_group', 'units_available', 'last_updated']
    list_editable = ['units_available']
    search_fields = ['blood_group']
    ordering = ['blood_group']
