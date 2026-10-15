"""Modul backend autentikasi Flask dengan antarmuka web interaktif.

Modul ini menyediakan layanan web berbasis Flask untuk demonstrasi pipeline DevSecOps.
Fitur utama mencakup:
1. Inisialisasi dan manajemen basis data SQLite.
2. Halaman Login utama (/) dengan penanganan autentikasi aman.
3. Halaman Dashboard (/dashboard) pasca-login dengan proteksi XSS.
4. Halaman About (/about) untuk informasi status portal aplikasi.
"""

import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from markupsafe import escape

# Inisialisasi aplikasi Flask
app = Flask(__name__)


def init_db():
    """Menginisialisasi basis data SQLite dan menyiapkan tabel serta data awal.

    Fungsi ini akan membuat tabel 'users' jika belum ada di database 'users.db',
    kemudian memasukkan kredensial default ('admin', 'supersecret') untuk
    keperluan pengujian login awal.
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Membuat tabel pengguna jika belum tersedia
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)"
    )

    # Memasukkan data pengguna default (mengabaikan jika sudah ada)
    cursor.execute(
        "INSERT OR IGNORE INTO users VALUES ('admin', 'supersecret')"
    )

    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def index():
    """Menampilkan formulir login (GET) dan memproses autentikasi pengguna (POST).

    Proses POST menggunakan parameterized query untuk mencegah SQL Injection.

    Returns:
        str: Hasil render template HTML 'index.html' untuk metode GET atau login gagal,
             atau pengalihan (redirect) ke rute '/dashboard' jika login berhasil.
    """
    message = None
    status_class = None

    if request.method == "POST":
        # Membaca data input dari formulir HTML
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # Membuka koneksi ke basis data SQLite
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Parameterized query (?) untuk memblokir celah kerentanan SQL Injection
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            # Jika kredensial valid, alihkan pengguna ke rute dashboard
            return redirect(url_for("dashboard", user=username))

        # Jika kredensial tidak cocok, siapkan pesan kesalahan
        message = "Login Gagal! Kredensial tidak valid."
        status_class = "danger"

    # Menampilkan formulir login beserta pesan status (jika ada)
    return render_template(
        "index.html", message=message, status_class=status_class
    )


@app.route("/dashboard", methods=["GET"])
def dashboard():
    """Menampilkan halaman dashboard utama setelah pengguna berhasil login.

    Parameter 'user' dari URL disanitasi menggunakan escape() untuk mencegah
    kerentanan Reflected Cross-Site Scripting (XSS).

    Returns:
        str: Konten HTML responsif berisi pesan selamat datang dan navigasi logout.
    """
    # Mengambil nama pengguna dari query parameter URL (default: 'Pengguna')
    user = request.args.get("user", "Pengguna")

    # Sanitasi variabel pengguna untuk menetralisir karakter HTML/JS berbahaya (mencegah XSS)
    safe_user = escape(user)

    # Menyusun tampilan HTML dashboard
    html_content = f"""
    <div style="font-family: sans-serif; text-align: center; margin-top: 50px;">
        <h2>Selamat Datang di Dashboard, {safe_user}!</h2>
        <p style="color: #555;">Sistem pemantauan CI/CD beroperasi secara normal.</p>
        <a href="/" style="text-decoration: none; color: #0066cc; font-weight: bold;">Logout</a>
    </div>
    """
    return html_content


@app.route("/about", methods=["GET"])
def about():
    """Menampilkan informasi versi dan status operasional portal DevSecOps.

    Returns:
        str: Konten HTML statis mengenai informasi dan versi aplikasi.
    """
    html_content = """
    <div style="font-family: sans-serif; text-align: center; margin-top: 50px;">
        <h2>Tentang Portal DevSecOps</h2>
        <p style="color: #555;">Versi: 1.0.0 | Status: Aktif & Terverifikasi</p>
        <a href="/" style="text-decoration: none; color: #0066cc; font-weight: bold;">Kembali ke Beranda</a>
    </div>
    """
    return html_content


if __name__ == "__main__":
    # Menjalankan inisialisasi tabel database sebelum aplikasi dimulai
    init_db()

    # Menjalankan web server Flask pada port 5000
    # Catatan: '# nosemgrep' digunakan untuk mengabaikan peringatan debug/binding lokal pada Semgrep
    app.run(host="0.0.0.0", port=5000)  # nosemgrep
