from generator.font_loader import get_font_path


# ---------------------------------------------------------
# VALIDATE LAYOUT
# ---------------------------------------------------------
def validate_layout(layout):
    errors = []

    # Layout must be a dict with "fields"
    if not isinstance(layout, dict) or "fields" not in layout:
        return ["Layout missing 'fields' section"]

    fields = layout.get("fields", {})
    if not isinstance(fields, dict):
        return ["Layout 'fields' must be an object"]

    for name, field in fields.items():

        # Field must be a dict
        if not isinstance(field, dict):
            errors.append(f"Field '{name}' is not a valid object")
            continue

        # Required keys
        for key in ["x", "y", "size", "font", "color", "align"]:
            if key not in field:
                errors.append(f"Field '{name}' missing required key '{key}'")

        # Coordinates
        if field.get("x", 0) < 0 or field.get("y", 0) < 0:
            errors.append(f"Field '{name}' has negative coordinates")

        # Font exists
        font_name = field.get("font")
        if font_name and not get_font_path(font_name):
            errors.append(f"Font '{font_name}' for field '{name}' does not exist")

        # Alignment
        if field.get("align") not in ["left", "center", "right"]:
            errors.append(f"Field '{name}' has invalid alignment '{field.get('align')}'")

        # Color (hex only)
        color = field.get("color", "")
        if not (isinstance(color, str) and color.startswith("#") and len(color) in [4, 7]):
            errors.append(f"Field '{name}' has invalid color '{color}'")

    return errors


# ---------------------------------------------------------
# VALIDATE DATA ROW
# ---------------------------------------------------------
def validate_data_row(row, layout):
    errors = []

    fields = layout.get("fields", {})

    for field in fields:
        if field not in row:
            errors.append(f"Missing field '{field}' in data row")
            continue

        value = row.get(field, "")
        if value is None or str(value).strip() == "":
            errors.append(f"Field '{field}' is empty")

    return errors


# ---------------------------------------------------------
# VALIDATE BEFORE RENDERING
# ---------------------------------------------------------
def validate_before_render(template_id, layout, data):
    errors = []

    # Layout validation
    errors.extend(validate_layout(layout))

    # Data validation
    errors.extend(validate_data_row(data, layout))

    return errors
