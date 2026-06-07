from django.contrib import admin

from .models import VehicleMovement


@admin.register(VehicleMovement)
class VehicleMovementAdmin(admin.ModelAdmin):
    list_display = ('vehicle_number', 'delivery', 'driver_name', 'transporter_name', 'vehicle_status', 'transport_payment_status')
    list_filter = ('vehicle_status', 'transport_payment_status')
    search_fields = ('vehicle_number', 'delivery__delivery_reference_code', 'lr_number', 'e_way_bill_number')
