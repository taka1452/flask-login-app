from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret_key"  # セッションの暗号鍵（適当な文字列でOK）
DB_FILE = "database.db"

# DB初期化（ユーザーテーブル追加）
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT
            )
        """)
        # 初回だけテストユーザー作成
        conn.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", "pass"))

@app.route("/", methods=["GET"])
def index():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html", user=session["user"])

@app.route("/login", methods=["GET", "POST"])
def login():
    init_db()

    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = cur.fetchone()
            if user:
                session["user"] = username
                return redirect("/")
            else:
                error = "ユーザー名またはパスワードが違います"

    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            return redirect("/login")  # 登録後ログイン画面へ
        except sqlite3.IntegrityError:
            error = "そのユーザー名はすでに登録されています"

    return render_template("register.html", error=error)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
