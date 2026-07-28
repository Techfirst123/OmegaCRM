from core.import_utils import to_int_or_none
from core.models import MaterialMaster


def _clean_text(value):
    return str(value or '').strip()


def _matching_materials(material_name, unit):
    return list(
        MaterialMaster.objects.filter(
            material_name__iexact=material_name,
            qty_specification__iexact=unit,
        ).order_by('id')
    )


def normalize_bulk_rows(raw_rows):
    normalized = []
    for raw in raw_rows:
        normalized.append({
            'material_name': _clean_text(raw.get('material_name')),
            'unit': _clean_text(raw.get('unit')),
            'quantity': to_int_or_none(raw.get('quantity')),
        })
    return normalized


def check_bulk_rows(raw_rows):
    """Check imported product+quantity rows against current MaterialMaster stock.

    Returns (result_rows, all_matched). result_rows carry the normalized
    material_name/unit/requested_qty so the caller can re-run the same
    check later without trusting client-supplied match state.
    """
    rows = normalize_bulk_rows(raw_rows)
    result_rows = []
    all_matched = bool(rows)

    for row in rows:
        material_name, unit, quantity = row['material_name'], row['unit'], row['quantity']
        result = {
            'material_name': material_name,
            'unit': unit,
            'requested_qty': quantity,
            'available_qty': None,
            'matched': False,
            'reason': '',
        }
        if not material_name:
            result['reason'] = 'Material name is required.'
        elif not unit:
            result['reason'] = 'Unit is required.'
        elif quantity is None or quantity <= 0:
            result['reason'] = 'Quantity must be a whole number greater than zero.'
        else:
            candidates = _matching_materials(material_name, unit)
            available = sum((candidate.qty or 0) for candidate in candidates)
            result['available_qty'] = available
            if not candidates:
                result['reason'] = 'Material not found in inventory.'
            elif available < quantity:
                result['reason'] = f'Insufficient stock (available: {available}).'
            else:
                result['matched'] = True
                result['reason'] = 'Available in inventory.'

        if not result['matched']:
            all_matched = False
        result_rows.append(result)

    return result_rows, all_matched


def deduct_material_stock(material_name, unit, quantity):
    """Consume `quantity` from matching MaterialMaster rows (oldest first).

    Returns the first material row stock was taken from, or None if nothing
    matched (caller is expected to have already confirmed a match exists).
    """
    remaining = quantity
    primary_material = None
    for material in _matching_materials(material_name, unit):
        if remaining <= 0:
            break
        available = material.qty or 0
        if available <= 0:
            continue
        take = min(available, remaining)
        material.qty = available - take
        material.save(update_fields=['qty'])
        remaining -= take
        if primary_material is None:
            primary_material = material
    return primary_material
