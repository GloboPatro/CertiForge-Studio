import os
import json
from datetime import datetime
from generator.path_utils import get_template_folder


DEFAULT_METADATA = {
    "name": None,  # will be replaced by folder name
    "description": "",
    "tags": [],
    "category": "general",
    "author": "unknown",
    "version": "1.0",
    "created_at": None,
    "orientation": "landscape"
}


def load_metadata(template_id):
    """
    Loads metadata.json for a template.
    If missing, creates a default metadata file.
    """
    folder = get_template_folder(template_id)
    if not folder:
        return None

    metadata_path = os.path.join(folder, "metadata.json")

    # If metadata doesn't exist, generate default
    if not os.path.exists(metadata_path):
        meta = DEFAULT_METADATA.copy()
        meta["name"] = template_id.replace("_", " ").title()
        meta["created_at"] = datetime.utcnow().isoformat()
        save_metadata(template_id, meta)
        return meta

    # Load existing metadata safely
    try:
         with open(metadata_path, "r", encoding="utf-8") as f:
             meta = json.load(f)

         # AUTO‑REPAIR: fix missing or invalid name
         if not meta.get("name") or meta.get("name") == "Untitled Template":
            meta["name"] = template_id.replace("_", " ").title()
            save_metadata(template_id, meta)

         return meta
    except Exception:
        # If metadata is corrupted, regenerate it
        meta = DEFAULT_METADATA.copy()
        meta["name"] = template_id.replace("_", " ").title()
        meta["created_at"] = datetime.utcnow().isoformat()
        save_metadata(template_id, meta)
        return meta


def save_metadata(template_id, metadata):
    """
    Saves metadata.json for a template.
    """
    folder = get_template_folder(template_id)
    if not folder:
        return False

    metadata_path = os.path.join(folder, "metadata.json")

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

    return True
