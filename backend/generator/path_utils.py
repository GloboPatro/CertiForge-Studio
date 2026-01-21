import os

# Absolute path to backend/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(BASE_DIR)


def get_template_folder(template_id):
    """
    Returns the absolute folder path for a template_id.
    Checks:
    - backend/templates_store/<template_id>
    - backend/uploads/templates/<template_id>
    """
    # Built-in templates
    builtin = os.path.join(BACKEND_DIR, "templates_store", template_id)
    if os.path.isdir(builtin):
        return builtin

    # User-uploaded templates
    uploaded = os.path.join(BACKEND_DIR, "uploads", "templates", template_id)
    if os.path.isdir(uploaded):
        return uploaded

    return None
