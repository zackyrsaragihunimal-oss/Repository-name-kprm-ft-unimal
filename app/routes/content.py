from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import News, Announcement, Document, Gallery
from ..extensions import db
from ..utils.audit import log_activity
from ..utils.upload import save_file, allowed_image, allowed_document
from datetime import datetime
import re

content_bp = Blueprint('content', __name__)

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

# === NEWS ===
@content_bp.route('/news')
@login_required
def news_index():
    news = News.query.order_by(News.created_at.desc()).all()
    return render_template('admin/news/index.html', news_list=news)

@content_bp.route('/news/create', methods=['GET', 'POST'])
@login_required
def news_create():
    if request.method == 'POST':
        thumb = None
        if 'thumbnail' in request.files:
            f = request.files['thumbnail']
            if f and allowed_image(f.filename):
                thumb = save_file(f, 'news')
        n = News(title=request.form.get('title', '').strip(), slug=slugify(request.form.get('title', '')),
                 content=request.form.get('content', ''), thumbnail=thumb,
                 category=request.form.get('category', 'umum'), author_id=current_user.id,
                 status=request.form.get('status', 'draft'),
                 published_at=datetime.utcnow() if request.form.get('status') == 'published' else None)
        db.session.add(n)
        db.session.commit()
        log_activity('Menambah berita', 'news', n.id)
        flash('Berita ditambahkan.', 'success')
        return redirect(url_for('content.news_index'))
    return render_template('admin/news/form.html', news=None)

@content_bp.route('/news/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def news_edit(id):
    n = News.query.get_or_404(id)
    if request.method == 'POST':
        if 'thumbnail' in request.files:
            f = request.files['thumbnail']
            if f and f.filename and allowed_image(f.filename):
                n.thumbnail = save_file(f, 'news')
        n.title = request.form.get('title', '').strip()
        n.slug = slugify(n.title)
        n.content = request.form.get('content', '')
        n.category = request.form.get('category', 'umum')
        n.status = request.form.get('status', 'draft')
        if n.status == 'published' and not n.published_at:
            n.published_at = datetime.utcnow()
        db.session.commit()
        log_activity('Mengedit berita', 'news', n.id)
        flash('Berita diperbarui.', 'success')
        return redirect(url_for('content.news_index'))
    return render_template('admin/news/form.html', news=n)

@content_bp.route('/news/delete/<int:id>', methods=['POST'])
@login_required
def news_delete(id):
    n = News.query.get_or_404(id)
    log_activity('Menghapus berita', 'news', n.id)
    db.session.delete(n)
    db.session.commit()
    flash('Berita dihapus.', 'success')
    return redirect(url_for('content.news_index'))

# === ANNOUNCEMENTS ===
@content_bp.route('/announcements')
@login_required
def ann_index():
    anns = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('admin/announcements/index.html', announcements=anns)

@content_bp.route('/announcements/create', methods=['GET', 'POST'])
@login_required
def ann_create():
    if request.method == 'POST':
        a = Announcement(title=request.form.get('title', '').strip(), content=request.form.get('content', ''),
                         priority=request.form.get('priority', 0, type=int), is_active=True,
                         start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date() if request.form.get('start_date') else None,
                         end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date() if request.form.get('end_date') else None)
        db.session.add(a)
        db.session.commit()
        log_activity('Menambah pengumuman', 'announcement', a.id)
        flash('Pengumuman ditambahkan.', 'success')
        return redirect(url_for('content.ann_index'))
    return render_template('admin/announcements/form.html', announcement=None)

@content_bp.route('/announcements/delete/<int:id>', methods=['POST'])
@login_required
def ann_delete(id):
    a = Announcement.query.get_or_404(id)
    db.session.delete(a)
    db.session.commit()
    flash('Pengumuman dihapus.', 'success')
    return redirect(url_for('content.ann_index'))

# === DOCUMENTS ===
@content_bp.route('/documents')
@login_required
def doc_index():
    docs = Document.query.order_by(Document.created_at.desc()).all()
    return render_template('admin/documents/index.html', documents=docs)

@content_bp.route('/documents/create', methods=['GET', 'POST'])
@login_required
def doc_create():
    if request.method == 'POST':
        fp = None
        if 'file' in request.files:
            f = request.files['file']
            if f and allowed_document(f.filename):
                fp = save_file(f, 'documents')
        d = Document(title=request.form.get('title', '').strip(), description=request.form.get('description', ''),
                     file_path=fp, category=request.form.get('category', 'regulasi'), uploaded_by=current_user.id)
        db.session.add(d)
        db.session.commit()
        log_activity('Menambah dokumen', 'document', d.id)
        flash('Dokumen ditambahkan.', 'success')
        return redirect(url_for('content.doc_index'))
    return render_template('admin/documents/form.html', document=None)

@content_bp.route('/documents/delete/<int:id>', methods=['POST'])
@login_required
def doc_delete(id):
    d = Document.query.get_or_404(id)
    db.session.delete(d)
    db.session.commit()
    flash('Dokumen dihapus.', 'success')
    return redirect(url_for('content.doc_index'))

# === GALLERY ===
@content_bp.route('/gallery')
@login_required
def gallery_index():
    items = Gallery.query.order_by(Gallery.created_at.desc()).all()
    return render_template('admin/gallery/index.html', items=items)

@content_bp.route('/gallery/create', methods=['GET', 'POST'])
@login_required
def gallery_create():
    if request.method == 'POST':
        ip = None
        if 'image' in request.files:
            f = request.files['image']
            if f and allowed_image(f.filename):
                ip = save_file(f, 'gallery')
        g = Gallery(title=request.form.get('title', '').strip(), description=request.form.get('description', ''),
                    image_path=ip, category=request.form.get('category', 'kegiatan'), uploaded_by=current_user.id)
        db.session.add(g)
        db.session.commit()
        flash('Foto ditambahkan.', 'success')
        return redirect(url_for('content.gallery_index'))
    return render_template('admin/gallery/form.html', item=None)

@content_bp.route('/gallery/delete/<int:id>', methods=['POST'])
@login_required
def gallery_delete(id):
    g = Gallery.query.get_or_404(id)
    db.session.delete(g)
    db.session.commit()
    flash('Foto dihapus.', 'success')
    return redirect(url_for('content.gallery_index'))
