from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from ..models import Candidate, CandidateProgram, Coalition, ElectionPeriod
from ..extensions import db
from ..utils.audit import log_activity
from ..utils.upload import save_file, allowed_image

candidates_bp = Blueprint('candidates', __name__)

@candidates_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    candidates = Candidate.query.order_by(Candidate.candidate_number).paginate(page=page, per_page=20)
    return render_template('admin/candidates/index.html', candidates=candidates)

@candidates_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        photo_path = None
        if 'photo' in request.files:
            f = request.files['photo']
            if f and allowed_image(f.filename):
                photo_path = save_file(f, 'candidates')
        candidate = Candidate(
            election_period_id=request.form.get('election_period_id', type=int),
            coalition_id=request.form.get('coalition_id', type=int) or None,
            candidate_number=request.form.get('candidate_number', type=int),
            name=request.form.get('name', '').strip(),
            nim=request.form.get('nim', '').strip(),
            photo=photo_path, position=request.form.get('position', 'Ketua BEM FT'),
            vision=request.form.get('vision', ''), mission=request.form.get('mission', ''),
            biography=request.form.get('biography', ''), status=request.form.get('status', 'draft')
        )
        db.session.add(candidate)
        db.session.commit()
        # Programs
        titles = request.form.getlist('program_title[]')
        descs = request.form.getlist('program_desc[]')
        for i, t in enumerate(titles):
            if t.strip():
                db.session.add(CandidateProgram(candidate_id=candidate.id, title=t.strip(), description=descs[i] if i < len(descs) else '', priority=i+1))
        db.session.commit()
        log_activity('Menambah kandidat', 'candidate', candidate.id)
        flash('Kandidat berhasil ditambahkan.', 'success')
        return redirect(url_for('candidates.index'))
    elections = ElectionPeriod.query.all()
    coalitions = Coalition.query.filter_by(is_active=True).all()
    return render_template('admin/candidates/form.html', candidate=None, elections=elections, coalitions=coalitions)

@candidates_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    candidate = Candidate.query.get_or_404(id)
    if request.method == 'POST':
        if 'photo' in request.files:
            f = request.files['photo']
            if f and f.filename and allowed_image(f.filename):
                candidate.photo = save_file(f, 'candidates')
        candidate.name = request.form.get('name', '').strip()
        candidate.nim = request.form.get('nim', '').strip()
        candidate.candidate_number = request.form.get('candidate_number', type=int)
        candidate.coalition_id = request.form.get('coalition_id', type=int) or None
        candidate.position = request.form.get('position', '')
        candidate.vision = request.form.get('vision', '')
        candidate.mission = request.form.get('mission', '')
        candidate.biography = request.form.get('biography', '')
        candidate.status = request.form.get('status', 'draft')
        db.session.commit()
        log_activity('Mengedit kandidat', 'candidate', candidate.id)
        flash('Kandidat diperbarui.', 'success')
        return redirect(url_for('candidates.index'))
    elections = ElectionPeriod.query.all()
    coalitions = Coalition.query.filter_by(is_active=True).all()
    return render_template('admin/candidates/form.html', candidate=candidate, elections=elections, coalitions=coalitions)

@candidates_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    c = Candidate.query.get_or_404(id)
    log_activity('Menghapus kandidat', 'candidate', c.id)
    CandidateProgram.query.filter_by(candidate_id=c.id).delete()
    db.session.delete(c)
    db.session.commit()
    flash('Kandidat dihapus.', 'success')
    return redirect(url_for('candidates.index'))
