import os, uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_IMG = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_DOC = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}

def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMG

def allowed_document(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in (ALLOWED_IMG | ALLOWED_DOC)

def save_file(file, subfolder=''):
    if not file or file.filename == '':
        return None
    ext = file.filename.rsplit('.', 1)[1].lower()
    safe_name = f"{uuid.uuid4().hex}.{ext}"
    folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, safe_name)
    file.save(filepath)
    return f"{subfolder}/{safe_name}" if subfolder else safe_name

def delete_file(filepath):
    if filepath:
        full = os.path.join(current_app.config['UPLOAD_FOLDER'], filepath)
        if os.path.exists(full):
            os.remove(full)
