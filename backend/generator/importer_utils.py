import os
import json
import zipfile
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_STORE = BASE_DIR / "templates_store"

def ensure_unique_id(base_id: str) -> str:
    candidate = base_id
    counter = 2
    while (TEMPLATES_STORE / candidate).exists():
        candidate = f"{base_id}_{counter}"
        counter += 1
    return candidate

def create_template_folder(template_id: str) -> Path:
    folder = TEMPLATES_STORE / template_id
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def generate_default_metadata(template_id: str, width: int, height: int) -> dict:
    return {
        "id": template_id,
        "name": template_id.replace("_", " ").title(),
        "width": width,
        "height": height,
        "description": "",
        "created": None
    }

def generate_default_layout(width: int, height: int) -> dict:
    return {
        "canvas": {"width": width, "height": height},
        "fields": {}
    }

def save_json(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_thumbnail(template_path: Path, thumb_path: Path, max_size=(400, 400)):
    img = Image.open(template_path)
    img.thumbnail(max_size)
    img.save(thumb_path, "JPEG", quality=85)

def import_from_zip(zip_file, original_filename: str) -> str:
    base_name = os.path.splitext(original_filename)[0]
    template_id = ensure_unique_id(base_name)
    folder = create_template_folder(template_id)

    temp_zip_path = folder / "upload.zip"
    zip_file.save(temp_zip_path)

    with zipfile.ZipFile(temp_zip_path, "r") as z:
        z.extractall(folder)

    temp_zip_path.unlink(missing_ok=True)

    template_img = None
    for name in ["template.png", "template.jpg", "template.jpeg"]:
        candidate = folder / name
        if candidate.exists():
            template_img = candidate
            break
    if template_img is None:
        raise ValueError("No template image (template.png/jpg) found in ZIP")

    with Image.open(template_img) as im:
        width, height = im.size

    metadata_path = folder / "metadata.json"
    if metadata_path.exists():
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    else:
        metadata = generate_default_metadata(template_id, width, height)
        save_json(metadata_path, metadata)

    layout_path = folder / "default_layout.json"
    if layout_path.exists():
        pass
    else:
        layout = generate_default_layout(width, height)
        save_json(layout_path, layout)

    thumb_path = folder / "thumb.jpg"
    if not thumb_path.exists():
        generate_thumbnail(template_img, thumb_path)

    return template_id

def import_from_image(image_file, original_filename: str) -> str:
    base_name = os.path.splitext(original_filename)[0]
    template_id = ensure_unique_id(base_name)
    folder = create_template_folder(template_id)

    ext = os.path.splitext(original_filename)[1].lower()
    if ext not in [".png", ".jpg", ".jpeg"]:
        ext = ".png"
    template_path = folder / f"template{ext}"
    image_file.save(template_path)

    with Image.open(template_path) as im:
        width, height = im.size

    metadata = generate_default_metadata(template_id, width, height)
    save_json(folder / "metadata.json", metadata)

    layout = generate_default_layout(width, height)
    save_json(folder / "default_layout.json", layout)

    thumb_path = folder / "thumb.jpg"
    generate_thumbnail(template_path, thumb_path)

    return template_id
