import os
from generator.layout_loader import load_layout
from generator.render import render_certificate
from generator.validator import validate_before_render
from generator.path_utils import BACKEND_DIR


def generate_single(template_id, data):
    """
    Generates a single certificate image object.
    Returns:
      - PIL.Image object on success
      - {"errors": [...]} on validation failure
    """
    layout = load_layout(template_id)

    errors = validate_before_render(template_id, layout, data)
    if errors:
        return {"errors": errors}

    # Correct indentation: this must run when NO errors
    img = render_certificate(template_id, layout, data)
    return img


def generate_bulk(template_id, rows, output_dir=None):
    """
    Generates multiple certificates from a list of data rows.
    Saves each certificate as a PNG file.
    Returns a list of:
      { "row": i, "file": "..."} or { "row": i, "errors": [...] }
    """
    if output_dir is None:
        output_dir = os.path.join(BACKEND_DIR, "output")

    os.makedirs(output_dir, exist_ok=True)

    results = []

    for i, row in enumerate(rows, start=1):
        result = generate_single(template_id, row)

        # Validation error
        if isinstance(result, dict) and "errors" in result:
            results.append({"row": i, "errors": result["errors"]})
            continue

        # Save certificate
        filename = os.path.join(output_dir, f"certificate_{i}.png")
        result.save(filename)

        results.append({"row": i, "file": filename})

    return results
