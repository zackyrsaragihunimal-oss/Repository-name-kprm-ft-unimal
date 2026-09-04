from flask import Blueprint, render_template, send_from_directory, current_app
from ..models import *
from ..extensions import db
import os

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def home():
    election = ElectionPeriod.query.order_by(ElectionPeriod.id.desc()).first()
    candidates = Candidate.query.filter_by(status='approved').order_by(Candidate.candidate_number).all() if election else []
    phases = ElectionPhase.query.filter_by(election_period_id=election.id).order_by(ElectionPhase.order_number).all() if election else []
    news = News.query.filter_by(status='published').order_by(News.published_at.desc()).limit(3).all()
    announcements = Announcement.query.filter_by(is_active=True).order_by(Announcement.priority.desc()).limit(3).all()
    stats = {
        'voters': Student.query.count(),
        'candidates': len(candidates),
        'coalitions': Coalition.query.count(),
    }
    return render_template('public/home.html', election=election, candidates=candidates, phases=phases, news=news, announcements=announcements, stats=stats)

@public_bp.route('/profil')
def about():
    return render_template('public/about.html')

@public_bp.route('/tahapan')
def phases():
    election = ElectionPeriod.query.order_by(ElectionPeriod.id.desc()).first()
    phases = ElectionPhase.query.filter_by(election_period_id=election.id).order_by(ElectionPhase.order_number).all() if election else []
    return render_template('public/phases.html', election=election, phases=phases)

@public_bp.route('/kandidat')
def candidates():
    election = ElectionPeriod.query.order_by(ElectionPeriod.id.desc()).first()
    candidates = Candidate.query.filter_by(status='approved').order_by(Candidate.candidate_number).all() if election else []
    return render_template('public/candidates.html', candidates=candidates, election=election)

@public_bp.route('/kandidat/<int:id>')
def candidate_detail(id):
    candidate = Candidate.query.get_or_404(id)
    programs = CandidateProgram.query.filter_by(candidate_id=id).order_by(CandidateProgram.priority).all()
    return render_template('public/candidate_detail.html', candidate=candidate, programs=programs)

@public_bp.route('/koalisi')
def coalitions():
    coalitions = Coalition.query.filter_by(is_active=True).all()
    return render_template('public/coalitions.html', coalitions=coalitions)

@public_bp.route('/pemilih')
def voters_info():
    election = ElectionPeriod.query.order_by(ElectionPeriod.id.desc()).first()
    total = Student.query.count()
    registered = VoterRegistration.query.filter_by(election_period_id=election.id).count() if election else 0
    return render_template('public/voters_info.html', election=election, total=total, registered=registered)

@public_bp.route('/berita')
def news():
    page = request.args.get('page', 1, type=int) if hasattr(__builtins__, '__import__') else 1
    from flask import request as req
    page = req.args.get('page', 1, type=int)
    news = News.query.filter_by(status='published').order_by(News.published_at.desc()).paginate(page=page, per_page=9)
    return render_template('public/news.html', news=news)

@public_bp.route('/berita/<slug>')
def news_detail(slug):
    article = News.query.filter_by(slug=slug).first_or_404()
    return render_template('public/news_detail.html', article=article)

@public_bp.route('/pengumuman')
def announcements():
    anns = Announcement.query.filter_by(is_active=True).order_by(Announcement.priority.desc()).all()
    return render_template('public/announcements.html', announcements=anns)

@public_bp.route('/dokumentasi')
def gallery():
    items = Gallery.query.order_by(Gallery.created_at.desc()).all()
    return render_template('public/gallery.html', items=items)

@public_bp.route('/regulasi')
def regulations():
    docs = Document.query.order_by(Document.created_at.desc()).all()
    return render_template('public/regulations.html', documents=docs)

@public_bp.route('/hasil')
def results():
    election = ElectionPeriod.query.order_by(ElectionPeriod.id.desc()).first()
    candidates = []
    total_votes = valid = invalid = 0
    if election:
        total_votes = Vote.query.filter_by(election_period_id=election.id).count()
        valid = Vote.query.filter_by(election_period_id=election.id, is_valid=True).count()
        invalid = Vote.query.filter_by(election_period_id=election.id, is_valid=False).count()
        for c in Candidate.query.filter_by(election_period_id=election.id, status='approved').order_by(Candidate.candidate_number).all():
            cv = Vote.query.filter_by(election_period_id=election.id, candidate_id=c.id, is_valid=True).count()
            candidates.append({'candidate': c, 'votes': cv, 'pct': round(cv/valid*100, 1) if valid > 0 else 0})
    total_registered = VoterRegistration.query.filter_by(election_period_id=election.id).count() if election else 0
    participation = round((Vote.query.filter_by(election_period_id=election.id).count() / total_registered * 100), 1) if total_registered > 0 and election else 0
    return render_template('public/results.html', election=election, candidates=candidates, total_votes=total_votes, valid=valid, invalid=invalid, total_registered=total_registered, participation=participation)

@public_bp.route('/live-counting')
def live_counting():
    return render_template('public/live_counting.html')

@public_bp.route('/transparansi')
def transparency():
    election = ElectionPeriod.query.order_by(ElectionPeriod.id.desc()).first()
    phases = ElectionPhase.query.filter_by(election_period_id=election.id).order_by(ElectionPhase.order_number).all() if election else []
    return render_template('public/transparency.html', election=election, phases=phases)

@public_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
