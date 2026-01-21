import os
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

from generator.font_loader import get_font_path
from generator.path_utils import get_template_folder, BACKEND_DIR


# ---------------------------------------------------------
# TEXT SHAPING (Arabic + bidi)
# ---------------------------------------------------------
def shape_text(text):
    """
    Applies Arabic shaping + bidi support.
    Works for both Arabic and non-Arabic text.
    """
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text


# ---------------------------------------------------------
# FONT LOADING (built-in + user + fallback)
# ---------------------------------------------------------
def load_font(font_name, size):
    """
    Loads a font from built-in or user fonts.
    Falls back to DejaVuSans if missing.
    """
    path = get_font_path(font_name)

    if path and os.path.exists(path):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass

    # fallback
    fallback = os.path.join(BACKEND_DIR, "fonts", "DejaVuSans.ttf")
    return ImageFont.truetype(fallback, size)


# ---------------------------------------------------------
# AUTO FONT SCALING
# ---------------------------------------------------------
def fit_text_to_width(draw, text, font_name, size, max_width):
    """
    Reduces font size until text fits within max_width.
    """
    while size > 10:
        font = load_font(font_name, size)
        w = draw.textlength(text, font=font)
        if w <= max_width:
            return font
        size -= 2

    return load_font(font_name, 10)  # minimum size


# ---------------------------------------------------------
# TEXT WRAPPING
# ---------------------------------------------------------
def wrap_text(draw, text, font, max_width):
    """
    Wraps text into multiple lines based on max_width.
    """
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = current + " " + word if current else word
        w = draw.textlength(test, font=font)

        if w <= max_width:
            current = test
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


# ---------------------------------------------------------
# DRAW TEXT WITH ALIGNMENT
# ---------------------------------------------------------
def draw_text(draw, text, x, y, font, color, align, image_width):
    """
    Draws text with alignment support.
    """
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]

    if align == "center":
        x = x - w // 2
    elif align == "right":
        x = x - w

    draw.text((x, y), text, font=font, fill=color)


# ---------------------------------------------------------
# MAIN RENDER FUNCTION
# ---------------------------------------------------------
def render_certificate(template_id, layout, data):
    """
    Renders a certificate using:
    - template.png
    - layout.json
    - data fields
    Returns a Pillow Image object.
    """
    folder = get_template_folder(template_id)
    if not folder:
        raise FileNotFoundError(f"Template '{template_id}' not found")

    template_path = os.path.join(folder, "template.png")
    image = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(image)
    image_width, _ = image.size

    for field_name, field in layout["fields"].items():
        if field_name not in data:
            continue

        text = str(data[field_name]).strip()
        if not text:
            continue

        shaped = shape_text(text)

        # Layout settings
        font_name = field.get("font", "DejaVuSans.ttf")
        size = field.get("size", 48)
        color = field.get("color", "#000000")
        align = field.get("align", "left")
        x = field.get("x", 0)
        y = field.get("y", 0)

        max_width = field.get("max_width", None)
        auto_scale = field.get("auto_scale", True)
        wrap = field.get("wrap", False)

        # Auto-scale if max_width is defined
        if max_width and auto_scale:
            font = fit_text_to_width(draw, shaped, font_name, size, max_width)
        else:
            font = load_font(font_name, size)

        # Wrapping
        if wrap and max_width:
            lines = wrap_text(draw, shaped, font, max_width)
            line_height = font.getbbox("Ay")[3] + 5

            for i, line in enumerate(lines):
                draw_text(draw, line, x, y + i * line_height, font, color, align, image_width)
        else:
            draw_text(draw, shaped, x, y, font, color, align, image_width)

    return image
