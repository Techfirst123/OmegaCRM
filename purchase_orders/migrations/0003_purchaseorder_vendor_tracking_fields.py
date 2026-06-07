from django.db import migrations, models


def backfill_vendor_tracking(apps, schema_editor):
    PurchaseOrder = apps.get_model('purchase_orders', 'PurchaseOrder')
    for po in PurchaseOrder.objects.select_related('vendor').all():
        vendor = po.vendor
        po.vendor_tracking_id = getattr(vendor, 'vendor_id', '') or ''
        po.vendor_tracking_name = getattr(vendor, 'vendor_name', '') or getattr(vendor, 'company_name', '') or ''
        po.save(update_fields=['vendor_tracking_id', 'vendor_tracking_name'])


class Migration(migrations.Migration):

    dependencies = [
        ('purchase_orders', '0002_purchaseorder_delivery_address_and_dispatch_origin'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='vendor_tracking_id',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='vendor_tracking_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.RunPython(backfill_vendor_tracking, migrations.RunPython.noop),
    ]
