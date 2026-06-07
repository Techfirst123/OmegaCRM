from decimal import Decimal

from django.db import models


class VehicleMovement(models.Model):
    PAYMENT_PENDING = 'pending'
    PAYMENT_APPROVED = 'approved'
    PAYMENT_PAID = 'paid'
    PAYMENT_HOLD = 'hold'
    TRANSPORT_PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, 'Pending'),
        (PAYMENT_APPROVED, 'Approved'),
        (PAYMENT_PAID, 'Paid'),
        (PAYMENT_HOLD, 'Hold'),
    ]

    STATUS_DISPATCHED = 'dispatched'
    STATUS_IN_TRANSIT = 'in_transit'
    STATUS_REACHED_SITE = 'reached_site'
    STATUS_UNLOADED = 'unloaded'
    STATUS_DELAYED = 'delayed'
    VEHICLE_STATUS_CHOICES = [
        (STATUS_DISPATCHED, 'Dispatched'),
        (STATUS_IN_TRANSIT, 'In Transit'),
        (STATUS_REACHED_SITE, 'Reached Site'),
        (STATUS_UNLOADED, 'Unloaded'),
        (STATUS_DELAYED, 'Delayed'),
    ]

    delivery = models.ForeignKey('deliveries.Delivery', on_delete=models.CASCADE, related_name='vehicles')
    vehicle_number = models.CharField(max_length=50)
    vehicle_type = models.CharField(max_length=80, blank=True)
    driver_name = models.CharField(max_length=120, blank=True)
    driver_mobile_number = models.CharField(max_length=20, blank=True)
    transporter_name = models.CharField(max_length=150, blank=True)
    lr_number = models.CharField(max_length=120, blank=True)
    e_way_bill_number = models.CharField(max_length=120, blank=True)
    dispatch_date = models.DateField(null=True, blank=True)
    expected_arrival_date = models.DateField(null=True, blank=True)
    actual_arrival_date = models.DateField(null=True, blank=True)
    gps_tracking_link = models.URLField(blank=True)
    loading_location = models.CharField(max_length=255, blank=True)
    unloading_location = models.CharField(max_length=255, blank=True)
    freight_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    transport_payment_status = models.CharField(
        max_length=20,
        choices=TRANSPORT_PAYMENT_STATUS_CHOICES,
        default=PAYMENT_PENDING,
    )
    vehicle_status = models.CharField(max_length=20, choices=VEHICLE_STATUS_CHOICES, default=STATUS_DISPATCHED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-dispatch_date', '-id']

    def __str__(self):
        return f'{self.vehicle_number} - {self.delivery.delivery_reference_code}'
