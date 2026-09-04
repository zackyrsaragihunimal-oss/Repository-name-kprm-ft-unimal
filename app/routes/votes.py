from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from ..models import (
    Vote,
    VoteRecapitulation,
    Candidate,
    PollingStation,
    ElectionPeriod,
    VoterRegistration,
    Student
)

from ..extensions import db
from ..utils.audit import log_activity
from ..utils.export import export_csv

from datetime import datetime


# =========================================================
# BLUEPRINT
# =========================================================

votes_bp = Blueprint('votes', __name__)
public_votes_bp = Blueprint('public_votes', __name__)


# =========================================================
# HALAMAN OPERATOR - TPS & REKAPITULASI
# URL: /admin/votes/
# =========================================================

@votes_bp.route('/')
@login_required
def index():

    election = ElectionPeriod.query.order_by(
        ElectionPeriod.id.desc()
    ).first()

    candidates = []
    tps_list = []

    if election:
        candidates = Candidate.query.filter_by(
            election_period_id=election.id,
            status='approved'
        ).order_by(
            Candidate.candidate_number
        ).all()

        tps_list = PollingStation.query.filter_by(
            election_period_id=election.id
        ).all()

    total_votes = Vote.query.count()

    valid = Vote.query.filter_by(
        is_valid=True
    ).count()

    invalid = Vote.query.filter_by(
        is_valid=False
    ).count()

    return render_template(
        'admin/votes/index.html',
        election=election,
        candidates=candidates,
        tps_list=tps_list,
        total_votes=total_votes,
        valid=valid,
        invalid=invalid
    )


# =========================================================
# PEMUNGUTAN SUARA INDIVIDUAL
# URL: /votes/cast
# =========================================================

@public_votes_bp.route('/cast', methods=['GET', 'POST'])
def cast_vote():

    election = ElectionPeriod.query.order_by(
        ElectionPeriod.id.desc()
    ).first()

    if not election:
        return render_template(
            'public/vote.html',
            election=None,
            candidates=[]
        )

    candidates = Candidate.query.filter_by(
        election_period_id=election.id,
        status='approved'
    ).order_by(
        Candidate.candidate_number
    ).all()

    if request.method == 'POST':

        nim = request.form.get(
            'nim',
            ''
        ).strip()

        candidate_id = request.form.get(
            'candidate_id',
            type=int
        )

        # =================================================
        # VALIDASI NIM
        # =================================================

        if not nim:
            flash(
                'NIM wajib diisi.',
                'danger'
            )

            return render_template(
                'public/vote.html',
                election=election,
                candidates=candidates
            )

        student = Student.query.filter_by(
            nim=nim
        ).first()

        if not student:
            flash(
                'NIM tidak ditemukan dalam daftar pemilih.',
                'danger'
            )

            return render_template(
                'public/vote.html',
                election=election,
                candidates=candidates
            )

        # =================================================
        # CEK KELAYAKAN
        # =================================================

        if not student.is_eligible:
            flash(
                'Pemilih tidak memenuhi syarat untuk menggunakan hak suara.',
                'danger'
            )

            return render_template(
                'public/vote.html',
                election=election,
                candidates=candidates
            )

        # =================================================
        # CEK REGISTRASI
        # =================================================

        registration = VoterRegistration.query.filter_by(
            student_id=student.id,
            election_period_id=election.id,
            is_registered=True
        ).first()

        if not registration:
            flash(
                'Anda belum terdaftar sebagai pemilih pada periode pemilihan ini.',
                'danger'
            )

            return render_template(
                'public/vote.html',
                election=election,
                candidates=candidates
            )

        # =================================================
        # ANTI DOUBLE VOTING
        # =================================================

        if registration.has_voted:

            waktu = ''

            if registration.voted_at:
                waktu = registration.voted_at.strftime(
                    '%d-%m-%Y %H:%M:%S'
                )

            flash(
                'Anda sudah menggunakan hak suara pada periode ini.'
                + (f' Waktu voting: {waktu}' if waktu else ''),
                'warning'
            )

            return render_template(
                'public/vote.html',
                election=election,
                candidates=candidates
            )

        # =================================================
        # VALIDASI KANDIDAT
        # =================================================

        if not candidate_id:

            flash(
                'Silakan pilih kandidat terlebih dahulu.',
                'danger'
            )

            return render_template(
                'public/vote.html',
                election=election,
                candidates=candidates
            )

        candidate = Candidate.query.filter_by(
            id=candidate_id,
            election_period_id=election.id,
            status='approved'
        ).first()

        if not candidate:

            flash(
                'Kandidat tidak valid.',
                'danger'
            )

            return render_template(
                'public/vote.html',
                election=election,
                candidates=candidates
            )

        # =================================================
        # TPS PEMILIH
        # =================================================

        tps = None

        if registration.polling_station_id:

            tps = PollingStation.query.filter_by(
                id=registration.polling_station_id,
                election_period_id=election.id
            ).first()

        if not tps:

            flash(
                'TPS pemilih belum ditentukan. Silakan hubungi operator KPRM.',
                'danger'
            )

            return render_template(
                'public/vote.html',
                election=election,
                candidates=candidates
            )

        # =================================================
        # TRANSAKSI ANTI DOUBLE VOTING
        # =================================================

        try:

            updated = VoterRegistration.query.filter_by(
                id=registration.id,
                has_voted=False
            ).update(
                {
                    'has_voted': True,
                    'voted_at': datetime.utcnow()
                },
                synchronize_session=False
            )

            if updated != 1:

                db.session.rollback()

                flash(
                    'Hak suara sudah digunakan atau proses voting sedang berlangsung.',
                    'warning'
                )

                return render_template(
                    'public/vote.html',
                    election=election,
                    candidates=candidates
                )

            # =================================================
            # SIMPAN SUARA
            # =================================================

            vote = Vote(
                election_period_id=election.id,
                polling_station_id=tps.id,
                candidate_id=candidate.id,
                is_valid=True,
                voted_at=datetime.utcnow()
            )

            db.session.add(vote)

            db.session.commit()

            flash(
                'Suara berhasil disimpan. Terima kasih telah menggunakan hak pilih Anda.',
                'success'
            )

            return render_template(
                'public/vote.html',
                election=election,
                candidates=candidates,
                vote_success=True
            )

        except Exception as e:

            db.session.rollback()

            print(
                'ERROR PEMUNGUTAN SUARA:',
                str(e)
            )

            flash(
                'Voting gagal diproses. Tidak ada perubahan yang disimpan.',
                'danger'
            )

            return render_template(
                'public/vote.html',
                election=election,
                candidates=candidates
            )

    return render_template(
        'public/vote.html',
        election=election,
        candidates=candidates
    )


# =========================================================
# INPUT SUARA OPERATOR
# URL: /admin/votes/input
# =========================================================

@votes_bp.route('/input', methods=['POST'])
@login_required
def input_vote():

    try:

        election = ElectionPeriod.query.order_by(
            ElectionPeriod.id.desc()
        ).first()

        if not election:

            flash(
                'Tidak ada periode pemilihan.',
                'danger'
            )

            return redirect(
                url_for('votes.index')
            )

        election_id = election.id

        tps_id = request.form.get(
            'polling_station_id',
            type=int
        )

        candidate_id = request.form.get(
            'candidate_id',
            type=int
        )

        is_valid = request.form.get(
            'is_valid',
            'true'
        ) == 'true'

        count = request.form.get(
            'count',
            1,
            type=int
        )

        if count < 1:

            flash(
                'Jumlah suara harus minimal 1.',
                'danger'
            )

            return redirect(
                url_for('votes.index')
            )

        if not tps_id:

            flash(
                'TPS wajib dipilih.',
                'danger'
            )

            return redirect(
                url_for('votes.index')
            )

        tps = PollingStation.query.filter_by(
            id=tps_id,
            election_period_id=election_id
        ).first()

        if not tps:

            flash(
                'TPS tidak valid untuk periode pemilihan ini.',
                'danger'
            )

            return redirect(
                url_for('votes.index')
            )

        if tps.status != 'active':

            flash(
                'TPS tersebut tidak sedang aktif.',
                'danger'
            )

            return redirect(
                url_for('votes.index')
            )

        candidate = None

        if is_valid:

            if not candidate_id:

                flash(
                    'Kandidat wajib dipilih untuk suara sah.',
                    'danger'
                )

                return redirect(
                    url_for('votes.index')
                )

            candidate = Candidate.query.filter_by(
                id=candidate_id,
                election_period_id=election_id,
                status='approved'
            ).first()

            if not candidate:

                flash(
                    'Kandidat tidak valid atau belum disetujui.',
                    'danger'
                )

                return redirect(
                    url_for('votes.index')
                )

        else:

            candidate_id = None

        # =================================================
        # CEK KAPASITAS TPS
        # =================================================

        existing_votes = Vote.query.filter_by(
            election_period_id=election_id,
            polling_station_id=tps.id
        ).count()

        capacity = tps.capacity or 100

        if existing_votes + count > capacity:

            sisa = max(
                capacity - existing_votes,
                0
            )

            flash(
                f'Jumlah suara melebihi kapasitas TPS. '
                f'Sisa yang dapat dimasukkan: {sisa}.',
                'danger'
            )

            return redirect(
                url_for('votes.index')
            )

        # =================================================
        # SIMPAN SUARA
        # =================================================

        for _ in range(count):

            vote = Vote(
                election_period_id=election_id,
                polling_station_id=tps.id,
                candidate_id=candidate_id,
                is_valid=is_valid,
                voted_at=datetime.utcnow()
            )

            db.session.add(vote)

        db.session.commit()

        log_activity(
            f'Input {count} suara',
            'vote',
            None
        )

        flash(
            f'{count} suara berhasil diinput.',
            'success'
        )

        return redirect(
            url_for('votes.index')
        )

    except Exception as e:

        db.session.rollback()

        print(
            'ERROR INPUT SUARA:',
            str(e)
        )

        flash(
            'Gagal menyimpan suara. Perubahan dibatalkan.',
            'danger'
        )

        return redirect(
            url_for('votes.index')
        )


# =========================================================
# REKAPITULASI SUARA
# =========================================================

@votes_bp.route('/recapitulate', methods=['POST'])
@login_required
def recapitulate():

    try:

        election = ElectionPeriod.query.order_by(
            ElectionPeriod.id.desc()
        ).first()

        if not election:

            flash(
                'Tidak ada periode pemilihan aktif.',
                'danger'
            )

            return redirect(
                url_for('votes.index')
            )

        VoteRecapitulation.query.filter_by(
            election_period_id=election.id
        ).delete(
            synchronize_session=False
        )

        tps_list = PollingStation.query.filter_by(
            election_period_id=election.id
        ).all()

        candidates = Candidate.query.filter_by(
            election_period_id=election.id,
            status='approved'
        ).all()

        for tps in tps_list:

            invalid = Vote.query.filter_by(
                election_period_id=election.id,
                polling_station_id=tps.id,
                is_valid=False
            ).count()

            for cand in candidates:

                valid = Vote.query.filter_by(
                    election_period_id=election.id,
                    polling_station_id=tps.id,
                    candidate_id=cand.id,
                    is_valid=True
                ).count()

                recap = VoteRecapitulation(
                    election_period_id=election.id,
                    polling_station_id=tps.id,
                    candidate_id=cand.id,
                    valid_votes=valid,
                    invalid_votes=invalid,
                    total_votes=valid + invalid,
                    recapitulated_by=current_user.id
                )

                db.session.add(recap)

        db.session.commit()

        log_activity(
            'Melakukan rekapitulasi suara',
            'vote_recapitulation',
            election.id
        )

        flash(
            'Rekapitulasi selesai!',
            'success'
        )

        return redirect(
            url_for('votes.index')
        )

    except Exception as e:

        db.session.rollback()

        print(
            'ERROR REKAPITULASI:',
            str(e)
        )

        flash(
            'Gagal melakukan rekapitulasi. Perubahan dibatalkan.',
            'danger'
        )

        return redirect(
            url_for('votes.index')
        )


# =========================================================
# EXPORT REKAP
# =========================================================

@votes_bp.route('/export')
@login_required
def export():

    recaps = VoteRecapitulation.query.all()

    data = []

    for r in recaps:

        cand = Candidate.query.get(
            r.candidate_id
        )

        tps = PollingStation.query.get(
            r.polling_station_id
        )

        data.append(
            (
                tps.name if tps else '-',
                cand.name if cand else '-',
                r.valid_votes,
                r.invalid_votes,
                r.total_votes
            )
        )

    return export_csv(
        data,
        [
            'TPS',
            'Kandidat',
            'Suara Sah',
            'Suara Tidak Sah',
            'Total'
        ],
        'rekap_suara.csv'
    )