import os, shutil, sqlite3
from datetime import datetime
from flask import current_app

def create_backup():
    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if not os.path.exists(db_path):
        raise FileNotFoundError("Database file not found")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"backup_{timestamp}.db"
    backup_dir = current_app.config['BACKUP_FOLDER']
    os.makedirs(backup_dir, exist_ok=True)
    dest = os.path.join(backup_dir, filename)
    # Use SQLite backup API for consistency
    src_conn = sqlite3.connect(db_path)
    dst_conn = sqlite3.connect(dest)
    src_conn.backup(dst_conn)
    src_conn.close()
    dst_conn.close()
    size = os.path.getsize(dest)
    return filename, dest, size

def restore_backup(filepath):
    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if not os.path.exists(filepath):
        raise FileNotFoundError("Backup file not found")
    shutil.copy2(filepath, db_path)
    return True
