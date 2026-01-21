# certapp/generator/data_loader.py

import csv
import openpyxl


def normalize_header(h):
    """
    Normalizes header names:
    - lowercase
    - strip spaces
    - replace spaces with underscores
    """
    return h.strip().lower().replace(" ", "_")


def load_csv(path):
    """
    Loads CSV or TSV data.
    Automatically detects delimiter.
    """
    with open(path, "r", encoding="utf-8-sig") as f:
        sample = f.read(2048)
        f.seek(0)

        # Detect delimiter
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";"])
        reader = csv.DictReader(f, dialect=dialect)

        rows = []
        for row in reader:
            clean = {normalize_header(k): v.strip() for k, v in row.items() if k}
            if any(clean.values()):
                rows.append(clean)

        return rows


def load_xlsx(path):
    """
    Loads XLSX data using openpyxl.
    """
    wb = openpyxl.load_workbook(path)
    sheet = wb.active

    headers = [normalize_header(c.value) for c in sheet[1]]
    rows = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        if not any(row):
            continue

        clean = {}
        for i, value in enumerate(row):
            clean[headers[i]] = str(value).strip() if value is not None else ""

        rows.append(clean)

    return rows


def load_manual(data_dict):
    """
    Manual entry mode.
    Already a dict, just normalize keys.
    """
    return {normalize_header(k): v for k, v in data_dict.items()}
