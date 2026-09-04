# KPRM FT UNIMAL

**Komisi Pemilihan Raya Mahasiswa Fakultas Teknik Universitas Malikussaleh** adalah portal digital Pemira untuk informasi publik dan administrasi pemilihan mahasiswa.

## Fitur
Portal publik responsif (profil, tahapan, kandidat, koalisi, berita, pengumuman, galeri, regulasi, hasil, live counting, transparansi), dashboard admin, CRUD pemilih/kandidat/koalisi/himpunan/periode/fase/TPS/konten, input suara dan rekapitulasi, AJAX live counting 5 detik, pengaturan, backup, audit log, role admin/operator, dan CSRF pada form.

## Teknologi
Python 3.10+, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Migrate, SQLite/SQLAlchemy, Bootstrap 5.3, Chart.js, Font Awesome 6, dan Inter.

## Struktur
```
kprm/app/templates/{base.html,admin/,public/}
kprm/app/static/{css/style.css,js/main.js,js/live-counting.js}
kprm/seeders/seed.py | run.py | requirements.txt | .env.example
```

## Instalasi dan menjalankan
```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```
Buka `http://127.0.0.1:5000`. Untuk produksi gunakan HTTPS, WSGI server, secret key kuat, validasi upload, dan database terkelola.

## Seeder
```bash
python seeders/seed.py
```
Seeder membuat 2 role, permissions, akun, fakultas, 6 departemen, 6 himpunan, Pemira 2026 dengan 12 fase, 2 koalisi, 3 kandidat approved, 3 TPS, 15 mahasiswa, registrasi pemilih, suara, 3 berita, 3 pengumuman, dan pengaturan default.

## Kredensial demo
Akun administrator dan operator disediakan melalui proses seeding awal.
Gunakan kredensial yang telah dikonfigurasi secara aman dan ubah password sebelum deployment.

## Backup
Gunakan **Admin → Backup → Buat Backup**. Simpan hasil di lokasi aman, batasi akses download, dan jadwalkan backup berkala. Jangan commit database atau kredensial ke repositori publik.
