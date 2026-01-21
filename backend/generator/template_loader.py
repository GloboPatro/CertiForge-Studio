import os
import json
from PIL import Image

from generator.metadata_loader import load_metadata, save_metadata
from generator.metadata_loader import load_metadata
from generator.path_utils import BACKEND_DIR


# Absolute paths inside backend/
BUILTIN_TEMPLATES_DIR = os.path.join(BACKEND_DIR, "templates_store")
USER_TEMPLATES_DIR = os.path.join(BACKEND_DIR, "uploads", "templates")
REMOTE_TEMPLATES_FILE = os.path.join(BACKEND_DIR, "remote_templates.json")


def load_templates():
    """
    Loads all templates from:
    - built-in templates
    - user-uploaded templates
    - remote templates
    Returns a unified list of template metadata.
    """
    templates = []

    # Built-in templates
    templates += load_local_templates(BUILTIN_TEMPLATES_DIR, source="built_in")

    # User-uploaded templates
    templates += load_local_templates(USER_TEMPLATES_DIR, source="user")

    # Remote templates
    templates += load_remote_templates()

    return templates


def load_local_templates(base_dir, source):
    """
    Scans a directory for template folders.
    Each folder name becomes the template_id.
    """
    if not os.path.exists(base_dir):
        return []

    template_list = []

    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        if not os.path.isdir(folder_path):
            continue

        template_id = folder

        # Ensure thumbnail exists
        template_path = os.path.join(folder_path, "template.png")
        thumb_path = os.path.join(folder_path, "thumb.jpg")

        if os.path.exists(template_path) and not os.path.exists(thumb_path):
            generate_thumbnail(template_path, thumb_path)

        # Ensure layout exists and is valid
        layout_path = os.path.join(folder_path, "default_layout.json")
        if not os.path.exists(layout_path):
            create_blank_layout(layout_path)
        else:
            _auto_repair_layout(layout_path)

        # Load metadata (auto‑creates if missing)
        meta = load_metadata(template_id)

        # AUTO‑REPAIR: fix missing or invalid name
        if not meta.get("name") or meta.get("name") == "Untitled Template":
            meta["name"] = template_id.replace("_", " ").title()
            save_metadata(template_id, meta)

        template_list.append({
            "id": template_id,
            "name": meta.get("name", template_id.replace("_", " ").title()),
            "source": source,
            "thumb": f"/templates/{template_id}/thumb",
            "preview": f"/templates/{template_id}/preview",
            "tags": meta.get("tags", []),
            "category": meta.get("category", "general"),
            "orientation": meta.get("orientation", "landscape")
        })

    return template_list


def load_remote_templates():
    """
    Loads remote templates from remote_templates.json.
    """
    if not os.path.exists(REMOTE_TEMPLATES_FILE):
        return []

    with open(REMOTE_TEMPLATES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    templates = []
    for entry in data:
        template_id = entry["id"]

        # Load metadata (auto‑creates if missing)
        meta = load_metadata(template_id)

        # AUTO‑REPAIR: fix missing or invalid name
        if not meta.get("name") or meta.get("name") == "Untitled Template":
            meta["name"] = entry.get("name", template_id.replace("_", " ").title())
            save_metadata(template_id, meta)


        templates.append({
            "id": template_id,
            "name": meta.get("name", entry.get("name", template_id)),
            "source": "remote",
            "thumb": entry.get("thumb"),
            "preview": entry.get("preview"),
            "tags": meta.get("tags", []),
            "category": meta.get("category", "general"),
            "orientation": meta.get("orientation", "landscape")
        })

    return templates


def generate_thumbnail(template_path, thumb_path):
    """
    Creates a 300px-wide thumbnail for the template.
    Guaranteed to work unless the image is unreadable.
    """
    try:
        print(f"Generating thumbnail for: {template_path}")  # debug

        img = Image.open(template_path).convert("RGB")
        img.thumbnail((300, 300))

        # Ensure directory exists
        os.makedirs(os.path.dirname(thumb_path), exist_ok=True)

        img.save(thumb_path, "JPEG", quality=85)

        print(f"Thumbnail saved to: {thumb_path}")  # debug

    except Exception as e:
        print(f"[ERROR] Thumbnail generation failed for {template_path}: {e}")


def create_blank_layout(layout_path):
    """
    Creates a blank layout JSON file.
    """
    blank = {"fields": {}}
    with open(layout_path, "w", encoding="utf-8") as f:
        json.dump(blank, f, indent=4)


def _auto_repair_layout(layout_path):
     """Ensures layout JSON has a valid structure."""
     try:
         with open(layout_path, "r", encoding="utf-8") as f:
             layout = json.load(f)

         if not isinstance(layout, dict):
             raise ValueError("Layout is not a dict")

         if "fields" not in layout or not isinstance(layout["fields"], dict):
             layout["fields"] = {}

         with open(layout_path, "w", encoding="utf-8") as f:
             json.dump(layout, f, indent=4)

     except Exception:
         create_blank_layout(layout_path)
