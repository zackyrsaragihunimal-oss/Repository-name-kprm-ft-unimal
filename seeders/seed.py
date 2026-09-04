"""Seeder data demo KPRM FT UNIMAL. Jalankan: python seeders/seed.py"""

from datetime import date, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models import *


app = create_app()


def get(model, **kw):
    return model.query.filter_by(**kw).first()


def make(model, kw, defaults=None):
    row = get(model, **kw)

    if row is None:
        row = model(**kw, **(defaults or {}))
        db.session.add(row)

    return row


def passwd(user, password):
    if hasattr(user, "set_password"):
        user.set_password(password)
    elif hasattr(user, "password_hash"):
        user.password_hash = generate_password_hash(password)
    elif hasattr(user, "password"):
        user.password = generate_password_hash(password)


with app.app_context():

    # =========================================================
    # DATABASE
    # =========================================================
    db.create_all()

    # =========================================================
    # ROLE
    # =========================================================
    admin_role = make(
        Role,
        {"name": "admin"},
        {"description": "Administrator penuh"}
    )

    operator_role = make(
        Role,
        {"name": "operator"},
        {"description": "Operator data"}
    )

    # =========================================================
    # PERMISSIONS
    # =========================================================
    perms = []

    permission_names = [
        "dashboard.view",
        "voters.manage",
        "candidates.manage",
        "coalitions.manage",
        "organizations.manage",
        "elections.manage",
        "polling.manage",
        "votes.manage",
        "content.manage",
        "settings.manage",
        "backup.manage",
        "audit.view",
        "users.manage",
    ]

    for name in permission_names:
        perms.append(
            make(
                Permission,
                {"name": name},
                {"description": name}
            )
        )

    db.session.flush()

    # Admin mendapatkan semua permission
    for permission in perms:
        if (
            hasattr(admin_role, "permissions")
            and permission not in admin_role.permissions
        ):
            admin_role.permissions.append(permission)

    # Operator mendapatkan permission utama
    for permission in perms[:10]:
        if (
            hasattr(operator_role, "permissions")
            and permission not in operator_role.permissions
        ):
            operator_role.permissions.append(permission)

    # =========================================================
    # USER ADMIN
    # =========================================================
    admin = make(
        User,
        {"username": "admin"},
        {
            "email": "admin@kprm.unimal.ac.id",
            "full_name": "Administrator KPRM",
            "role_id": admin_role.id,
            "is_active": True,
        }
    )

    admin.role_id = admin_role.id
    passwd(admin, "admin123")

    # =========================================================
    # USER OPERATOR
    # =========================================================
    operator = make(
        User,
        {"username": "operator"},
        {
            "email": "operator@kprm.unimal.ac.id",
            "full_name": "Operator KPRM",
            "role_id": operator_role.id,
            "is_active": True,
        }
    )

    operator.role_id = operator_role.id
    passwd(operator, "operator123")

    # =========================================================
    # FAKULTAS
    # =========================================================
    faculty = make(
        Faculty,
        {"name": "Fakultas Teknik"},
        {"code": "FT"}
    )

    # Penting:
    # Flush agar faculty.id sudah tersedia
    db.session.flush()

    # =========================================================
    # JURUSAN
    # =========================================================
    names = [
        "Teknik Informatika",
        "Sistem Informasi",
        "Teknik Sipil",
        "Teknik Mesin",
        "Teknik Elektro",
        "Teknik Industri",
    ]

    codes = [
        "TI",
        "SI",
        "TS",
        "TM",
        "TE",
        "TIND",
    ]

    deps = []

    for name, code in zip(names, codes):

        department = make(
            Department,
            {"name": name},
            {
                "code": code,
                "faculty_id": faculty.id,
            }
        )

        deps.append(department)

    # Pastikan ID jurusan tersedia
    db.session.flush()

    # =========================================================
    # ORGANISASI / HIMPUNAN
    # =========================================================
    orgnames = [
        "HMTI",
        "HMSI",
        "HMTS",
        "HMM",
        "HMTE",
        "HMTI",
    ]

    orgs = []

    for department, name in zip(deps, orgnames):

        organization = make(
            Organization,
            {"name": name},
            {
                "code": name,
                "department_id": department.id,
                "is_active": True,
            }
        )

        orgs.append(organization)

    db.session.flush()

    # =========================================================
    # PERIODE PEMILIHAN
    # =========================================================
    election = make(
        ElectionPeriod,
        {"name": "Pemira 2026"},
        {
            "year": 2026,
            "description": "Pemilihan Raya Mahasiswa Fakultas Teknik 2026.",
            "status": "active",
            "start_date": date(2026, 3, 1),
            "end_date": date(2026, 5, 30),
        }
    )

    db.session.flush()

    # =========================================================
    # TAHAPAN PEMILIHAN
    # =========================================================
    phases = [
        "Pembentukan KPRM",
        "Penyusunan Peraturan",
        "Pendaftaran Pemilih",
        "Verifikasi Data Pemilih",
        "Pendaftaran Kandidat",
        "Verifikasi Kandidat",
        "Penetapan Kandidat",
        "Masa Kampanye",
        "Masa Tenang",
        "Pemungutan Suara",
        "Penghitungan Suara",
        "Penetapan Hasil",
    ]

    for i, name in enumerate(phases, 1):

        start_date = date(2026, 3, 1) + timedelta(days=(i - 1) * 7)

        make(
            ElectionPhase,
            {
                "election_period_id": election.id,
                "order_number": i,
            },
            {
                "name": name,
                "start_date": start_date,
                "end_date": start_date + timedelta(days=5),
                "status": (
                    "ongoing"
                    if i == 6
                    else (
                        "completed"
                        if i < 6
                        else "upcoming"
                    )
                ),
            }
        )

    # =========================================================
    # KOALISI
    # =========================================================
    coalitions = []

    coalition_data = [
        (
            "Teknik Bersatu",
            "TB",
            "#1B3A5C"
        ),
        (
            "Inovasi Teknik",
            "IT",
            "#C8A951"
        ),
    ]

    for name, code, color in coalition_data:

        coalition = make(
            Coalition,
            {"name": name},
            {
                "code": code,
                "color": color,
                "election_period_id": election.id,
                "is_active": True,
                "description": f"Koalisi {name} untuk Pemira FT UNIMAL.",
            }
        )

        coalitions.append(coalition)

    db.session.flush()

    # =========================================================
    # ANGGOTA KOALISI
    # =========================================================
    coalition_groups = [
        (coalitions[0], orgs[:3]),
        (coalitions[1], orgs[3:]),
    ]

    for coalition, organizations in coalition_groups:

        for organization in organizations:

            make(
                CoalitionMember,
                {
                    "coalition_id": coalition.id,
                    "organization_id": organization.id,
                },
                {
                    "role": "Anggota"
                }
            )

    db.session.flush()

    # =========================================================
    # KANDIDAT
    # =========================================================
    candidates = []

    candidate_data = [
        (
            1,
            "Ahmad Fauzan",
            "220101001",
            coalitions[0]
        ),
        (
            2,
            "Cut Meutia",
            "220201014",
            coalitions[1]
        ),
        (
            3,
            "Rizky Pratama",
            "220301022",
            coalitions[0]
        ),
    ]

    for number, name, nim, coalition in candidate_data:

        candidate = make(
            Candidate,
            {
                "election_period_id": election.id,
                "candidate_number": number,
            },
            {
                "name": name,
                "nim": nim,
                "coalition_id": coalition.id,
                "position": "Ketua dan Wakil BEM FT",
                "vision": (
                    "Membangun Fakultas Teknik yang "
                    "kolaboratif, adaptif, dan berprestasi."
                ),
                "mission": (
                    "Menguatkan pelayanan mahasiswa "
                    "dan transparansi organisasi."
                ),
                "biography": (
                    "Mahasiswa aktif Fakultas Teknik "
                    "yang berkomitmen berkontribusi."
                ),
                "status": "approved",
            }
        )

        candidates.append(candidate)

    db.session.flush()

    # =========================================================
    # PROGRAM KERJA KANDIDAT
    # =========================================================
    for candidate in candidates:

        make(
            CandidateProgram,
            {
                "candidate_id": candidate.id,
                "title": f"Program {candidate.candidate_number}A",
            },
            {
                "description": (
                    "Program kolaborasi dan pelayanan mahasiswa."
                ),
                "priority": 1,
            }
        )

        make(
            CandidateProgram,
            {
                "candidate_id": candidate.id,
                "title": f"Program {candidate.candidate_number}B",
            },
            {
                "description": (
                    "Program penguatan prestasi dan inovasi "
                    "Fakultas Teknik."
                ),
                "priority": 2,
            }
        )

    # =========================================================
    # TPS
    # =========================================================
    tps = []

    tps_data = [
        (
            "TPS-01",
            "TPS Gedung A",
            "Gedung A Fakultas Teknik",
            150,
        ),
        (
            "TPS-02",
            "TPS Gedung B",
            "Gedung B Fakultas Teknik",
            150,
        ),
        (
            "TPS-03",
            "TPS Laboratorium",
            "Kompleks Laboratorium Teknik",
            100,
        ),
    ]

    for code, name, location, capacity in tps_data:

        polling_station = make(
            PollingStation,
            {
                "election_period_id": election.id,
                "code": code,
            },
            {
                "name": name,
                "location": location,
                "capacity": capacity,
                "status": "active",
            }
        )

        tps.append(polling_station)

    db.session.flush()

    # =========================================================
    # DATA MAHASISWA
    # =========================================================
    students = []

    for i in range(1, 16):

        student = make(
            Student,
            {
                "nim": f"220{i:02d}{i:04d}"
            },
            {
                "name": f"Mahasiswa Teknik {i:02d}",
                "email": f"mahasiswa{i:02d}@unimal.ac.id",
                "department_id": deps[(i - 1) % 6].id,
                "semester": i % 8 + 1,
                "is_eligible": True,
            }
        )

        students.append(student)

    db.session.flush()

    # =========================================================
    # PENDAFTARAN PEMILIH
    # =========================================================
    for i, student in enumerate(students):

        make(
            VoterRegistration,
            {
                "election_period_id": election.id,
                "student_id": student.id,
            },
            {
                "polling_station_id": tps[i % 3].id,
                "is_registered": True,
                "has_voted": False,
            }
        )

    # =========================================================
    # DATA SUARA DEMO
    # =========================================================
    for i, candidate in enumerate(candidates):

        vote_count = [5, 4, 3][i]

        for _ in range(vote_count):

            make(
                Vote,
                {
                    "election_period_id": election.id,
                    "polling_station_id": tps[i].id,
                    "candidate_id": candidate.id,
                    "is_valid": True,
                },
                {}
            )

    # Suara tidak sah
    make(
        Vote,
        {
            "election_period_id": election.id,
            "polling_station_id": tps[2].id,
            "candidate_id": None,
            "is_valid": False,
        },
        {}
    )

    # =========================================================
    # BERITA
    # =========================================================
    news_data = [
        (
            "KPRM FT UNIMAL Resmi Membuka Tahapan Pemira 2026",
            "Kegiatan",
        ),
        (
            "Kenali Kandidat dan Gagasan Mereka",
            "Informasi",
        ),
        (
            "Jaga Pemira Tetap Jujur dan Berintegritas",
            "Edukasi",
        ),
    ]

    for title, category in news_data:

        make(
            News,
            {"title": title},
            {
                "content": (
                    f"{title}. Simak informasi Pemira "
                    "melalui portal resmi KPRM."
                ),
                "category": category,
                "status": "published",
                "author_id": admin.id,
            }
        )

    # =========================================================
    # PENGUMUMAN
    # =========================================================
    announcement_data = [
        ("Pendaftaran Pemilih Diperpanjang", 2),
        ("Jadwal Verifikasi Kandidat", 1),
        ("Gunakan Hak Pilihmu", 3),
    ]

    for title, priority in announcement_data:

        make(
            Announcement,
            {"title": title},
            {
                "content": (
                    f"{title}. Informasi selengkapnya "
                    "tersedia di portal KPRM."
                ),
                "priority": priority,
                "is_active": True,
                "start_date": date(2026, 3, 1),
                "end_date": date(2026, 5, 30),
            }
        )

    # =========================================================
    # SETTING WEBSITE
    # =========================================================
    settings = {
        "site_name": "KPRM FT UNIMAL",
        "site_subtitle": "Komisi Pemilihan Raya Mahasiswa",
        "site_slogan": "Suaramu, Masa Depan Kita.",
        "faculty_name": "Fakultas Teknik",
        "university_name": "Universitas Malikussaleh",
        "year_pemira": "2026",
        "election_status": "Pemira sedang berlangsung",
        "contact_email": "kprm@unimal.ac.id",
        "contact_phone": "+62 812 0000 0000",
        "footer_text": "© 2026 KPRM FT UNIMAL. Hak cipta dilindungi.",
    }

    for key, value in settings.items():

        make(
            Setting,
            {"key": key},
            {"value": value}
        )

    # =========================================================
    # SIMPAN DATABASE
    # =========================================================
    db.session.commit()

    print()
    print("==============================================")
    print("       SEED DATA BERHASIL DIBUAT")
    print("==============================================")
    print("Admin    : admin")
    print("Password : admin123")
    print("----------------------------------------------")
    print("Operator : operator")
    print("Password : operator123")
    print("==============================================")