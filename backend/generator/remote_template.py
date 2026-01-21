import os
import requests
from PIL import Image
from generator.path_utils import BACKEND_DIR
from generator.metadata_loader import save_metadata
from generator.layout_loader import create_blank_layout


def download_template(url, template_id):
    """
    Downloads a remote template PNG and stores it in:
    backend/uploads/templates/<template_id>/
    Also generates:
    - metadata.json
    - default_layout.json
    - thumb.jpg
    """
    folder = os.path.join(BACKEND_DIR, "uploads", "templates", template_id)
    os.makedirs(folder, exist_ok=True)

    template_path = os.path.join(folder, "template.png")
    thumb_path = os.path.join(folder, "thumb.jpg")
    layout_path = os.path.join(folder, "default_layout.json")

    # -------------------------
    # DOWNLOAD TEMPLATE
    # -------------------------
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return {"error": f"Failed to download template: {e}"}

    with open(template_path, "wb") as f:
        f.write(response.content)

    # -------------------------
    # GENERATE THUMBNAIL
    # -------------------------
    try:
        img = Image.open(template_path)
        img.thumbnail((300, 300))
        img.save(thumb_path, "JPEG")
    except Exception as e:
        return {"error": f"Template downloaded but thumbnail failed: {e}"}

    # -------------------------
    # CREATE METADATA
    # -------------------------
    metadata = {
        "name": template_id.replace("_", " ").title(),
        "description": "",
        "tags": [],
        "category": "general",
        "author": "remote",
        "version": "1.0",
        "orientation": "landscape"
    }
    save_metadata(template_id, metadata)

    # -------------------------
    # CREATE BLANK LAYOUT
    # -------------------------
    create_blank_layout(layout_path)

    return {
        "status": "ok",
        "template_id": template_id,
        "folder": folder,
        "preview": f"/templates/{template_id}/preview",
        "thumb": f"/templates/{template_id}/thumb"
    }
