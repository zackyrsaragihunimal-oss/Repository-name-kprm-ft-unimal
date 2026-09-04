from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import Student, Department, VoterRegistration, ElectionPeriod
from ..extensions import db
from ..utils.audit import log_activity
from ..utils.export import export_csv

voters_bp = Blueprint('voters', __name__)

@voters_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    query = Student.query
    if search:
        query = query.filter(Student.name.contains(search) | Student.nim.contains(search))
    students = query.order_by(Student.name).paginate(page=page, per_page=20)
    return render_template('admin/voters/index.html', students=students, search=search)

@voters_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        nim = request.form.get('nim', '').strip()
        if Student.query.filter_by(nim=nim).first():
            flash('NIM sudah terdaftar!', 'danger')
            return redirect(url_for('voters.create'))
        student = Student(
            nim=nim, name=request.form.get('name', '').strip(),
            email=request.form.get('email', '').strip(),
            phone=request.form.get('phone', '').strip(),
            department_id=request.form.get('department_id', type=int),
            semester=request.form.get('semester', type=int),
            is_eligible=bool(request.form.get('is_eligible'))
        )
        db.session.add(student)
        db.session.commit()
        log_activity('Menambah pemilih', 'student', student.id)
        flash('Pemilih berhasil ditambahkan.', 'success')
        return redirect(url_for('voters.index'))
    departments = Department.query.all()
    return render_template('admin/voters/form.html', departments=departments, student=None)

@voters_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.nim = request.form.get('nim', '').strip()
        student.name = request.form.get('name', '').strip()
        student.email = request.form.get('email', '').strip()
        student.phone = request.form.get('phone', '').strip()
        student.department_id = request.form.get('department_id', type=int)
        student.semester = request.form.get('semester', type=int)
        student.is_eligible = bool(request.form.get('is_eligible'))
        db.session.commit()
        log_activity('Mengedit pemilih', 'student', student.id)
        flash('Data pemilih diperbarui.', 'success')
        return redirect(url_for('voters.index'))
    departments = Department.query.all()
    return render_template('admin/voters/form.html', departments=departments, student=student)

@voters_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    student = Student.query.get_or_404(id)
    log_activity('Menghapus pemilih', 'student', student.id)
    db.session.delete(student)
    db.session.commit()
    flash('Pemilih dihapus.', 'success')
    return redirect(url_for('voters.index'))

@voters_bp.route('/export')
@login_required
def export():
    students = Student.query.order_by(Student.nim).all()
    data = [(s.nim, s.name, s.email, s.department.name if s.department else '-', s.semester, 'Ya' if s.is_eligible else 'Tidak') for s in students]
    return export_csv(data, ['NIM', 'Nama', 'Email', 'Program Studi', 'Semester', 'Eligible'], 'daftar_pemilih.csv')
