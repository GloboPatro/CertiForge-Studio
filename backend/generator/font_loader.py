import os
from generator.path_utils import BACKEND_DIR

# Absolute paths inside backend/
BUILTIN_FONTS_DIR = os.path.join(BACKEND_DIR, "fonts")
USER_FONTS_DIR = os.path.join(BACKEND_DIR, "uploads", "fonts")

VALID_EXTENSIONS = {".ttf", ".otf"}


def list_fonts():
    """
    Returns a list of all available fonts:
    - built-in fonts
    - user-uploaded fonts
    """
    fonts = []

    # Built-in fonts
    if os.path.exists(BUILTIN_FONTS_DIR):
        for f in os.listdir(BUILTIN_FONTS_DIR):
            if os.path.splitext(f)[1].lower() in VALID_EXTENSIONS:
                fonts.append({
                    "name": f,
                    "source": "built_in",
                    "path": os.path.join(BUILTIN_FONTS_DIR, f)
                })

    # User fonts
    if os.path.exists(USER_FONTS_DIR):
        for f in os.listdir(USER_FONTS_DIR):
            if os.path.splitext(f)[1].lower() in VALID_EXTENSIONS:
                fonts.append({
                    "name": f,
                    "source": "user",
                    "path": os.path.join(USER_FONTS_DIR, f)
                })

    return fonts


def get_font_path(font_name):
    """
    Returns the full path to a font file.
    Searches user fonts first, then built-in fonts.
    """
    user_path = os.path.join(USER_FONTS_DIR, font_name)
    builtin_path = os.path.join(BUILTIN_FONTS_DIR, font_name)

    if os.path.exists(user_path):
        return user_path

    if os.path.exists(builtin_path):
        return builtin_path

    return None
