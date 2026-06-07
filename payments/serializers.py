def serialize_payment(payment):
    return {
        'id': payment.id,
        'po_number': payment.po.po_number,
        'payment_reference_code': payment.payment_reference_code,
        'payment_stage': payment.payment_stage,
        'payment_amount': str(payment.payment_amount or 0),
        'net_payable': str(payment.net_payable or 0),
        'payment_status': payment.payment_status,
        'payment_due_date': payment.payment_due_date.isoformat() if payment.payment_due_date else '',
    }
