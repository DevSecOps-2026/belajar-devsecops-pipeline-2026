import sqlite3
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

def init_db():
    """Inisialisasi basis data dan membuat data pengguna awal."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users "
        "(username TEXT, password TEXT)"
    )

    cursor.execute(
        "INSERT OR IGNORE INTO users VALUES "
        "('admin', 'supersecret')"
    )

    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def index():
    """Menampilkan formulir login dan memproses autentikasi."""
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
            message = "Login Berhasil! Selamat datang."
            status_class = "success"
        else:
            message = "Login Gagal! Kredensial tidak valid."
            status_class = "danger"

    return render_template(
        "index.html",
        message=message,
        status_class=status_class,
    )


# @app.route("/sentinel/pulse")
# def sentinel_pulse():
#     """Menampilkan heartbeat sederhana dari aplikasi Sentinel."""
#     return jsonify(
#         {
#             "service": "Sentinel Flask Application",
#             "status": "operational",
#             "environment": "docker",
#             "pipeline": "github-actions",
#         }
#     )


# @app.route("/deployment-manifest")
# def deployment_manifest():
#     """Menampilkan informasi deployment aplikasi."""
#     return jsonify(
#         {
#             "application": "Sentinel Flask",
#             "version": "PBL-CICD-03",
#             "container": "secure-flask-app",
#             "deployment": "automatic",
#             "pipeline": "GitHub Actions",
#         }
#     )

@app.route("/register", methods=["GET", "POST"])
def register():
    """Menampilkan formulir registrasi dan memproses penambahan pengguna."""
    message = None
    status_class = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username and password:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            
            # Cek apakah username sudah ada di database
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                message = "Registrasi gagal! Username sudah digunakan."
                status_class = "danger"
            else:
                # Insert data pengguna baru menggunakan parameterized query
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)", 
                    (username, password)
                )
                conn.commit()
                message = "Registrasi Berhasil! Silakan kembali ke halaman login."
                status_class = "success"
                
            conn.close()
        else:
            message = "Username dan password tidak boleh kosong!"
            status_class = "warning"

    return render_template(
        "register.html", message=message, status_class=status_class
    )

@app.route("/dashboard")
def dashboard():
    """Menampilkan halaman dashboard untuk pengguna yang sudah login."""
    # Catatan: Di aplikasi nyata, Anda perlu mengecek session login di sini
    return render_template("dashboard.html")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)  # nosemgrep
    