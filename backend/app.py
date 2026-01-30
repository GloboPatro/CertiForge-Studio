from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
import os
import json
import webbrowser
import threading
import time
import io
import zipfile
import tempfile
import logging

from generator.template_loader import load_templates
from generator.layout_loader import load_layout
from generator.path_utils import get_template_folder
from generator.generate import generate_single, generate_bulk
from generator.remote_template import download_template
from generator.importer_utils import import_from_zip, import_from_image


app = Flask(__name__)
CORS(app)

# Base directory of backend/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger("certiforge")
logging.basicConfig(level=logging.INFO)


# ---------------------------------------------------------
# SERVE FRONTEND (index.html)
# ---------------------------------------------------------
@app.route("/")
def serve_frontend():
    frontend_path = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))
    return send_from_directory(frontend_path, "index.html")


# ---------------------------------------------------------
# SERVE ALL OTHER FRONTEND FILES (HTML, JS, CSS, IMAGES)
# ---------------------------------------------------------
@app.route("/<path:path>")
def serve_static_files(path):
    frontend_path = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))
    return send_from_directory(frontend_path, path)


# ---------------------------------------------------------
# LIST ALL TEMPLATES
# ---------------------------------------------------------
@app.route("/templates", methods=["GET"])
def api_list_templates():
    templates = load_templates()
    return jsonify({"templates": templates})


# ---------------------------------------------------------
# GET LAYOUT FOR TEMPLATE
# ---------------------------------------------------------
@app.route("/templates/<template_id>/layout", methods=["GET"])
def api_get_layout(template_id):
    layout = load_layout(template_id)
    return jsonify({"layout": layout})


# ---------------------------------------------------------
# SAVE LAYOUT FOR TEMPLATE
# ---------------------------------------------------------
@app.route("/templates/<template_id>/layout", methods=["POST"])
def api_save_layout(template_id):
    data = request.json
    folder = get_template_folder(template_id)

    if not folder:
        return jsonify({"error": "Template not found"}), 404

    layout_path = os.path.join(folder, "default_layout.json")

    with open(layout_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return jsonify({"status": "saved"})


# ---------------------------------------------------------
# GENERATE SINGLE CERTIFICATE
# ---------------------------------------------------------
@app.route("/generate/single", methods=["POST"])
def api_generate_single():
    payload = request.json

    template_id = payload.get("template_id")
    data = payload.get("data")

    if not template_id or not data:
        return jsonify({"error": "template_id and data are required"}), 400

    try:
        result = generate_single(template_id, data)
    except FileNotFoundError as e:
        logger.warning("Template not found: %s", e)
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.exception("Error generating single certificate")
        return jsonify({"error": "Server error during generation", "details": str(e)}), 500

    if isinstance(result, dict) and "errors" in result:
        return jsonify(result), 400

    img = result

    output_dir = os.path.join(BASE_DIR, "output")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "single_preview.png")
    try:
        img.save(output_path)
    except Exception as e:
        logger.exception("Failed to save generated image")
        return jsonify({"error": "Failed to save generated image", "details": str(e)}), 500

    return send_file(output_path, mimetype="image/png")


# ---------------------------------------------------------
# GENERATE BULK CERTIFICATES (returns ZIP)
# ---------------------------------------------------------
@app.route("/generate/bulk", methods=["POST"])
def api_generate_bulk():
    payload = request.json

    template_id = payload.get("template_id")
    rows = payload.get("rows")

    if not template_id or not rows:
        return jsonify({"error": "template_id and rows are required"}), 400

    # Use a temporary directory per-request to avoid disk accumulation
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            results = generate_bulk(template_id, rows, output_dir=tmpdir)
            # Build an in-memory ZIP with generated files + results.json
            mem = io.BytesIO()
            with zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                # Add generated images (only files that exist)
                for r in results:
                    if "file" in r:
                        fname = r["file"]
                        # file paths returned by generate_bulk are basenames relative to output_dir
                        fpath = os.path.join(tmpdir, fname)
                        if os.path.exists(fpath):
                            zf.write(fpath, arcname=fname)
                # Add results.json so caller can inspect per-row errors
                zf.writestr("results.json", json.dumps(results, indent=2))

            mem.seek(0)
            return send_file(
                mem,
                mimetype="application/zip",
                as_attachment=True,
                download_name="certificates.zip"
            )
    except FileNotFoundError as e:
        logger.warning("Template not found during bulk generation: %s", e)
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.exception("Error during bulk generation")
        return jsonify({"error": "Server error during bulk generation", "details": str(e)}), 500


# ---------------------------------------------------------
# IMPORT REMOTE TEMPLATE FROM URL
# ---------------------------------------------------------
@app.route("/templates/import", methods=["POST"])
def api_import_template():
    payload = request.json

    url = payload.get("url")
    template_id = payload.get("template_id")

    if not url or not template_id:
        return jsonify({"error": "url and template_id are required"}), 400

    result = download_template(url, template_id)

    if "error" in result:
        return jsonify(result), 400

    return jsonify(result)


# ---------------------------------------------------------
# IMPORT TEMPLATE FROM ZIP
# ---------------------------------------------------------
@app.route("/import/zip", methods=["POST"])
def api_import_zip():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        template_id = import_from_zip(file, file.filename)
        return jsonify({"template_id": template_id})
    except Exception as e:
        logger.exception("Error importing ZIP")
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------
# IMPORT TEMPLATE FROM IMAGE
# ---------------------------------------------------------
@app.route("/import/image", methods=["POST"])
def api_import_image():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        template_id = import_from_image(file, file.filename)
        return jsonify({"template_id": template_id})
    except Exception as e:
        logger.exception("Error importing image")
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------
# TEMPLATE PREVIEW (FULL IMAGE)
# ---------------------------------------------------------
@app.route("/templates/<template_id>/preview", methods=["GET"])
def api_template_preview(template_id):
    folder = get_template_folder(template_id)
    if not folder:
        return jsonify({"error": "Template not found"}), 404

    path = os.path.join(folder, "template.png")
    if not os.path.exists(path):
        return jsonify({"error": "template.png missing"}), 404

    return send_file(path, mimetype="image/png")


# ---------------------------------------------------------
# TEMPLATE THUMBNAIL
# ---------------------------------------------------------
@app.route("/templates/<template_id>/thumb", methods=["GET"])
def api_template_thumb(template_id):
    folder = get_template_folder(template_id)
    if not folder:
        return jsonify({"error": "Template not found"}), 404

    path = os.path.join(folder, "thumb.jpg")
    if not os.path.exists(path):
        return jsonify({"error": "thumb.jpg missing"}), 404

    return send_file(path, mimetype="image/jpeg")


# ---------------------------------------------------------
# SERVE BUILT-IN TEMPLATE FILES
# ---------------------------------------------------------
@app.route("/templates_store/<template_id>/<filename>")
def serve_builtin_template(template_id, filename):
    return send_from_directory(
        os.path.join(BASE_DIR, "templates_store", template_id),
        filename
    )


# ---------------------------------------------------------
# SERVE USER-UPLOADED TEMPLATE FILES
# ---------------------------------------------------------
@app.route("/uploads/templates/<template_id>/<filename>")
def serve_user_template(template_id, filename):
    return send_from_directory(
        os.path.join(BASE_DIR, "uploads", "templates", template_id),
        filename
    )


# ---------------------------------------------------------
# AUTO-OPEN BROWSER + RUN APP
# ---------------------------------------------------------
def open_browser():
    time.sleep(1)
    webbrowser.open("http://localhost:5000/")

if __name__ == "__main__":
    # Only open browser in the reloader's main process
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Thread(target=open_browser).start()

    app.run(debug=True)