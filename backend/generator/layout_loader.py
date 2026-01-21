import os
import json
from generator.path_utils import get_template_folder, BACKEND_DIR


REMOTE_TEMPLATES_FILE = os.path.join(BACKEND_DIR, "remote_templates.json")


def load_layout(template_id):
    """
    Loads the layout for a template.
    If missing, creates a blank layout.
    Supports built-in, user, and remote templates.
    """
    folder = get_template_folder(template_id)

    # -------------------------
    # LOCAL TEMPLATE (built-in or user)
    # -------------------------
    if folder:
        layout_path = os.path.join(folder, "default_layout.json")

        if not os.path.exists(layout_path):
            create_blank_layout(layout_path)

        try:
            with open(layout_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # Corrupted layout → regenerate
            create_blank_layout(layout_path)
            return {"fields": {}}

    # -------------------------
    # REMOTE TEMPLATE
    # -------------------------
    if os.path.exists(REMOTE_TEMPLATES_FILE):
        try:
            with open(REMOTE_TEMPLATES_FILE, "r", encoding="utf-8") as f:
                remote_data = json.load(f)
        except Exception:
            return {"fields": {}}

        for entry in remote_data:
            if entry["id"] == template_id:
                # If remote template has a layout, use it
                if "layout" in entry:
                    return entry["layout"]

                # Otherwise return blank layout
                return {"fields": {}}

    # -------------------------
    # TEMPLATE NOT FOUND
    # -------------------------
    return {"fields": {}}


def create_blank_layout(path):
    """
    Creates a blank layout JSON file.
    """
    blank = {"fields": {}}
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(blank, f, indent=4)
