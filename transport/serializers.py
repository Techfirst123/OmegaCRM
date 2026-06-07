def serialize_vehicle(vehicle):
    return {
        'id': vehicle.id,
        'vehicle_number': vehicle.vehicle_number,
        'vehicle_type': vehicle.vehicle_type,
        'driver_name': vehicle.driver_name,
        'transporter_name': vehicle.transporter_name,
        'vehicle_status': vehicle.vehicle_status,
        'freight_amount': str(vehicle.freight_amount or 0),
    }
