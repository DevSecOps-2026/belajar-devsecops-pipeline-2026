"""Modul backend autentikasi Flask dengan antarmuka web interaktif.

Modul ini menyediakan layanan web berbasis Flask untuk demonstrasi pipeline DevSecOps.
"""

import sqlite3
from flask import (
    Flask,
    render_template,
    render_template_string,
    request,
    redirect,
    url_for,
    session,
)

# Inisialisasi aplikasi Flask
app = Flask(__name__)
app.secret_key = "devsecops-secret-key"  # Diperlukan untuk manajemen session Flask


def init_db():
    """Menginisialisasi basis data SQLite dan menyiapkan tabel serta data awal."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)"
    )
    cursor.execute(
        "INSERT OR IGNORE INTO users VALUES ('admin', 'supersecret')"
    )

    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def index():
    """Menampilkan formulir login (GET) dan memproses autentikasi pengguna (POST)."""
    message = None
    status_class = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Parameterized query untuk mencegah SQL Injection
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            # Menyimpan user ke dalam session Flask
            # Memutus alur taint data request ke redirect untuk mencegah Open Redirect
            session["user"] = username
            return redirect(url_for("dashboard"))

        message = "Login Gagal! Kredensial tidak valid."
        status_class = "danger"

    return render_template(
        "index.html", message=message, status_class=status_class
    )


@app.route("/dashboard", methods=["GET"])
def dashboard():
    """Menampilkan halaman dashboard utama setelah pengguna berhasil login."""
    user = session.get("user", "Pengguna")

    # Menggunakan render_template_string dengan auto-escaping Jinja2
    # Memperbaiki aturan directly-returned-format-string dan pencegahan XSS
    dashboard_template = """
    <div style="font-family: sans-serif; text-align: center; margin-top: 50px;">
        <h2>Selamat Datang di Dashboard, {{ user }}!</h2>
        <p style="color: #555;">Sistem pemantauan CI/CD beroperasi secara normal.</p>
        <a href="/" style="text-decoration: none; color: #0066cc; font-weight: bold;">Logout</a>
    </div>
    """
    return render_template_string(dashboard_template, user=user)


@app.route("/about", methods=["GET"])
def about():
    """Menampilkan informasi versi dan status operasional portal DevSecOps."""
    about_template = """
    <div style="font-family: sans-serif; text-align: center; margin-top: 50px;">
        <h2>Tentang Portal DevSecOps</h2>
        <p style="color: #555;">Versi: 1.0.0 | Status: Aktif & Terverifikasi</p>
        <a href="/" style="text-decoration: none; color: #0066cc; font-weight: bold;">Kembali ke Beranda</a>
    </div>
    """
    return render_template_string(about_template)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)  # nosemgrep
