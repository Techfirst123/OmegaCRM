def serialize_delivery(delivery):
    return {
        'id': delivery.id,
        'po_number': delivery.po.po_number,
        'item': delivery.po_item.material_name,
        'delivery_reference_code': delivery.delivery_reference_code,
        'delivery_date': delivery.delivery_date.isoformat() if delivery.delivery_date else '',
        'delivered_quantity': str(delivery.delivered_quantity or 0),
        'pending_quantity_after_delivery': str(delivery.pending_quantity_after_delivery or 0),
        'delivery_status': delivery.delivery_status,
    }
