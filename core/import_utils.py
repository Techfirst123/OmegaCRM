import re
import zipfile
from decimal import Decimal, InvalidOperation
from io import BytesIO
from xml.etree import ElementTree as ET


def normalize_header(value):
    return re.sub(r'[^a-z0-9]+', '', str(value or '').lower())


def to_decimal_or_none(value):
    text = str(value or '').strip().replace(',', '')
    if not text:
        return None
    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        return None


def to_int_or_none(value):
    text = str(value or '').strip().replace(',', '')
    if not text:
        return None
    try:
        parsed = Decimal(text)
    except (InvalidOperation, ValueError):
        return None
    if parsed != parsed.to_integral_value():
        return None
    return int(parsed)


def _xlsx_column_to_index(column_ref):
    index = 0
    for char in column_ref:
        if char.isalpha():
            index = (index * 26) + (ord(char.upper()) - ord('A') + 1)
    return max(index - 1, 0)


def load_xlsx_rows(uploaded_file):
    uploaded_file.seek(0)
    file_bytes = uploaded_file.read()
    archive = zipfile.ZipFile(BytesIO(file_bytes))

    workbook_tree = ET.fromstring(archive.read('xl/workbook.xml'))
    workbook_rels_tree = ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))
    ns_main = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    ns_pkg = {'pkg': 'http://schemas.openxmlformats.org/package/2006/relationships'}

    sheets = workbook_tree.find('main:sheets', ns_main)
    if sheets is None or not list(sheets):
        return []

    first_sheet = list(sheets)[0]
    relationship_id = first_sheet.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
    rel_targets = {
        rel.attrib.get('Id'): rel.attrib.get('Target')
        for rel in workbook_rels_tree.findall('pkg:Relationship', ns_pkg)
    }
    sheet_target = rel_targets.get(relationship_id, 'worksheets/sheet1.xml').lstrip('/')
    sheet_path = sheet_target if sheet_target.startswith('xl/') else f"xl/{sheet_target}"

    shared_strings = []
    if 'xl/sharedStrings.xml' in archive.namelist():
        shared_tree = ET.fromstring(archive.read('xl/sharedStrings.xml'))
        for string_item in shared_tree.findall('main:si', ns_main):
            parts = [node.text or '' for node in string_item.findall('.//main:t', ns_main)]
            shared_strings.append(''.join(parts))

    sheet_tree = ET.fromstring(archive.read(sheet_path))
    rows = []
    for row_node in sheet_tree.findall('.//main:sheetData/main:row', ns_main):
        cells = {}
        max_index = -1
        for cell in row_node.findall('main:c', ns_main):
            cell_ref = cell.attrib.get('r', '')
            col_ref = ''.join(char for char in cell_ref if char.isalpha())
            col_index = _xlsx_column_to_index(col_ref)
            max_index = max(max_index, col_index)
            cell_type = cell.attrib.get('t')
            if cell_type == 'inlineStr':
                value = ''.join(node.text or '' for node in cell.findall('.//main:t', ns_main))
            else:
                value_node = cell.find('main:v', ns_main)
                raw_value = value_node.text if value_node is not None else ''
                if cell_type == 's':
                    try:
                        value = shared_strings[int(raw_value)]
                    except (ValueError, IndexError):
                        value = raw_value
                else:
                    value = raw_value
            cells[col_index] = value
        if max_index >= 0:
            rows.append([cells.get(index, '') for index in range(max_index + 1)])
    return rows
