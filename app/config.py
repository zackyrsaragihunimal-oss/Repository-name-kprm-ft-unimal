import os
from dotenv import load_dotenv

# Folder aplikasi
basedir = os.path.abspath(os.path.dirname(__file__))

# Folder utama project
project_root = os.path.dirname(basedir)

# Load .env dari folder utama project
load_dotenv(os.path.join(project_root, '.env'))

# Database utama KPRM
database_path = os.path.join(project_root, 'kprm.db')


class Config:

    # Secret key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kprm-ft-unimal-secret-key-2026'

    # PAKSA menggunakan database utama di folder project
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + database_path

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Folder upload
    UPLOAD_FOLDER = os.path.join(project_root, 'uploads')

    # Folder backup
    BACKUP_FOLDER = os.path.join(project_root, 'backups')

    # Maksimal upload 5 MB
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    # File gambar
    ALLOWED_EXTENSIONS = {
        'png',
        'jpg',
        'jpeg',
        'gif',
        'webp'
    }

    # File dokumen
    ALLOWED_DOC_EXTENSIONS = {
        'pdf',
        'doc',
        'docx',
        'xls',
        'xlsx',
        'ppt',
        'pptx'
    }

    # CSRF
    WTF_CSRF_ENABLED = True

    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'