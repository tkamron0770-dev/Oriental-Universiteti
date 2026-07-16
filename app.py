# -*- coding: utf-8 -*-
"""
Oliy ta'lim muassasasi — Oylik ish haqi hisoblash tizimi (veb-ilova).
Login/parol + rol bo'yicha dostup (admin / muharrir / ko'ruvchi).
Flask + SQLite. Bitta fayl, oson joylashtiriladi.
"""
import os, json, sqlite3, secrets
from functools import wraps
from flask import (Flask, request, session, redirect, url_for, render_template,
                   jsonify, abort, flash)
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "ish_haqi.db"))
app = Flask(__name__)

# ---------------- Ma'lumotlar bazasi ----------------
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db(); c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        pw_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'viewer',
        full_name TEXT DEFAULT '')""")
    c.execute("""CREATE TABLE IF NOT EXISTS kv(
        key TEXT PRIMARY KEY, value TEXT)""")
    conn.commit()

    # SECRET_KEY (sessiyalar qayta ishga tushgandan keyin ham ishlashi uchun bazada saqlanadi)
    sk = get_kv(c, "secret_key")
    if not sk:
        sk = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
        set_kv(c, "secret_key", sk); conn.commit()
    app.secret_key = os.environ.get("SECRET_KEY") or sk

    # Dastlabki admin
    c.execute("SELECT COUNT(*) AS n FROM users")
    if c.fetchone()["n"] == 0:
        c.execute("INSERT INTO users(username, pw_hash, role, full_name) VALUES(?,?,?,?)",
                  ("admin", generate_password_hash("admin123"), "admin", "Bosh administrator"))
        conn.commit()

    # Dastlabki ma'lumot (namuna)
    if not get_kv(c, "state"):
        set_kv(c, "state", json.dumps(SEED_STATE, ensure_ascii=False)); conn.commit()
    conn.close()

def get_kv(c, k):
    c.execute("SELECT value FROM kv WHERE key=?", (k,))
    r = c.fetchone()
    return r["value"] if r else None

def set_kv(c, k, v):
    c.execute("INSERT INTO kv(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (k, v))

# ---------------- Namuna boshlang'ich holat ----------------
SEED_STATE = {
    "settings": {"tax": 12, "inps": 0.1, "union": 1, "bhm": 412000},
    "lists": {
        "pos": ["Professor","Dotsent","Katta o'qituvchi","Assistent","O'qituvchi","Rektor","Prorektor",
                "Direktor","Dekan","Kafedra mudiri","Bo'lim boshlig'i","Bosh buxgalter","Katta buxgalter",
                "Buxgalter","Iqtisodchi","Kassir","Marketing bo'limi boshlig'i","Marketing menejeri","SMM menejer",
                "Kadrlar bo'limi boshlig'i","Kadrlar inspektori","Yurist","IT mutaxassisi","Bosh mutaxassis",
                "Mutaxassis","Inspektor","Kotib","Referent","Muhandis","Laborant","Ombor mudiri","Haydovchi",
                "Farrosh","Qorovul","Elektrik"],
        "deg": ["—","Fan nomzodi (PhD)","Fan doktori (DSc)","Dotsent","Professor","Katta ilmiy xodim","Magistr"],
        "dept": ["Rektorat","Dekanat","Buxgalteriya","Iqtisod bo'limi","Marketing bo'limi","Kadrlar bo'limi",
                 "O'quv bo'limi","Ilmiy bo'lim","IT bo'limi","Yuridik bo'lim","Xo'jalik bo'limi",
                 "Aniq fanlar kafedrasi","Ijtimoiy fanlar kafedrasi","Tillar kafedrasi","Xavfsizlik bo'limi"]
    },
    "employees": {
        "teachers": [
            {"id":1,"fio":"Karimov Alisher Baxtiyorovich","pos":"Professor","dept":"Aniq fanlar kafedrasi","deg":"Fan doktori (DSc)","stavka":1,"base":4200000,"hours":80,"rate":38000,"degp":30,"stajp":15,"bonus":1500000,"advance":0},
            {"id":2,"fio":"Rahimova Nodira Akmalovna","pos":"Dotsent","dept":"Tillar kafedrasi","deg":"Fan nomzodi (PhD)","stavka":1,"base":3600000,"hours":90,"rate":30000,"degp":20,"stajp":10,"bonus":1000000,"advance":500000},
            {"id":3,"fio":"Yusupov Bekzod Shavkatovich","pos":"Katta o'qituvchi","dept":"Ijtimoiy fanlar kafedrasi","deg":"Magistr","stavka":0.5,"base":3200000,"hours":60,"rate":25000,"degp":5,"stajp":5,"bonus":500000,"advance":0}
        ],
        "admin": [
            {"id":4,"fio":"To'xtayev Sardor Ilhomovich","pos":"Direktor","dept":"Rektorat","deg":"Fan nomzodi (PhD)","stavka":1,"base":6000000,"hours":0,"rate":0,"degp":25,"stajp":20,"bonus":2500000,"advance":0},
            {"id":5,"fio":"Aliyeva Gulnora Sobirovna","pos":"Bosh buxgalter","dept":"Buxgalteriya","deg":"—","stavka":1,"base":4500000,"hours":0,"rate":0,"degp":0,"stajp":20,"bonus":1500000,"advance":0},
            {"id":6,"fio":"Nazarov Otabek Qahramonovich","pos":"Buxgalter","dept":"Buxgalteriya","deg":"—","stavka":1,"base":3200000,"hours":0,"rate":0,"degp":0,"stajp":10,"bonus":600000,"advance":400000},
            {"id":7,"fio":"Sobirova Dilnoza Akmalovna","pos":"Marketing bo'limi boshlig'i","dept":"Marketing bo'limi","deg":"—","stavka":1,"base":3800000,"hours":0,"rate":0,"degp":0,"stajp":10,"bonus":900000,"advance":0},
            {"id":8,"fio":"Rustamov Jahongir Baxodirovich","pos":"Kadrlar bo'limi boshlig'i","dept":"Kadrlar bo'limi","deg":"—","stavka":1,"base":3500000,"hours":0,"rate":0,"degp":0,"stajp":15,"bonus":700000,"advance":0}
        ],
        "tech": [
            {"id":9,"fio":"Qodirov Jasur Otabekovich","pos":"Muhandis","dept":"Xo'jalik bo'limi","deg":"—","stavka":1,"base":2800000,"hours":0,"rate":0,"degp":0,"stajp":5,"bonus":300000,"advance":0},
            {"id":10,"fio":"Ergasheva Zilola Furqatovna","pos":"Laborant","dept":"O'quv bo'limi","deg":"—","stavka":1,"base":2400000,"hours":0,"rate":0,"degp":0,"stajp":0,"bonus":200000,"advance":0}
        ]
    },
    "nextId": 11
}

# ---------------- Auth yordamchilari ----------------
def current_user():
    uid = session.get("uid")
    if not uid: return None
    conn = db(); c = conn.cursor()
    c.execute("SELECT id, username, role, full_name FROM users WHERE id=?", (uid,))
    r = c.fetchone(); conn.close()
    return dict(r) if r else None

def login_required(f):
    @wraps(f)
    def w(*a, **k):
        if not session.get("uid"): return redirect(url_for("login"))
        return f(*a, **k)
    return w

def role_required(*roles):
    def deco(f):
        @wraps(f)
        def w(*a, **k):
            u = current_user()
            if not u: return redirect(url_for("login"))
            if u["role"] not in roles: abort(403)
            return f(*a, **k)
        return w
    return deco

# ---------------- Marshrutlar ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        un = request.form.get("username", "").strip()
        pw = request.form.get("password", "")
        conn = db(); c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (un,))
        r = c.fetchone(); conn.close()
        if r and check_password_hash(r["pw_hash"], pw):
            session["uid"] = r["id"]
            return redirect(url_for("index"))
        flash("Login yoki parol noto'g'ri.")
    if session.get("uid"): return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/change-password", methods=["POST"])
@login_required
def change_password():
    u = current_user()
    old = request.form.get("old",""); new = request.form.get("new","")
    conn = db(); c = conn.cursor()
    c.execute("SELECT pw_hash FROM users WHERE id=?", (u["id"],))
    r = c.fetchone()
    if not check_password_hash(r["pw_hash"], old):
        conn.close(); flash("Joriy parol noto'g'ri."); return redirect(url_for("users_page") if u["role"]=="admin" else url_for("index"))
    if len(new) < 5:
        conn.close(); flash("Yangi parol kamida 5 belgidan iborat bo'lsin."); return redirect(url_for("index"))
    c.execute("UPDATE users SET pw_hash=? WHERE id=?", (generate_password_hash(new), u["id"]))
    conn.commit(); conn.close(); flash("Parol o'zgartirildi.")
    return redirect(url_for("index"))

@app.route("/")
@login_required
def index():
    u = current_user()
    conn = db(); c = conn.cursor()
    state = json.loads(get_kv(c, "state")); conn.close()
    return render_template("app.html", state=json.dumps(state, ensure_ascii=False), user=u)

# ----- API: holatni saqlash -----
@app.route("/api/state", methods=["POST"])
@role_required("admin", "editor")
def api_state():
    """Xodimlar va ro'yxatlarni saqlaydi (muharrir va admin)."""
    payload = request.get_json(force=True)
    conn = db(); c = conn.cursor()
    state = json.loads(get_kv(c, "state"))
    if "employees" in payload: state["employees"] = payload["employees"]
    if "lists" in payload: state["lists"] = payload["lists"]
    if "nextId" in payload: state["nextId"] = payload["nextId"]
    set_kv(c, "state", json.dumps(state, ensure_ascii=False))
    conn.commit(); conn.close()
    return jsonify(ok=True)

@app.route("/api/settings", methods=["POST"])
@role_required("admin")
def api_settings():
    """Soliq/ushlanma stavkalari (faqat admin)."""
    payload = request.get_json(force=True)
    conn = db(); c = conn.cursor()
    state = json.loads(get_kv(c, "state"))
    state["settings"] = payload
    set_kv(c, "state", json.dumps(state, ensure_ascii=False))
    conn.commit(); conn.close()
    return jsonify(ok=True)

# ----- Foydalanuvchilarni boshqarish (admin) -----
@app.route("/users")
@role_required("admin")
def users_page():
    conn = db(); c = conn.cursor()
    c.execute("SELECT id, username, role, full_name FROM users ORDER BY id")
    users = [dict(r) for r in c.fetchall()]; conn.close()
    return render_template("users.html", users=users, user=current_user())

@app.route("/users/add", methods=["POST"])
@role_required("admin")
def users_add():
    un = request.form.get("username","").strip()
    pw = request.form.get("password","")
    role = request.form.get("role","viewer")
    fn = request.form.get("full_name","").strip()
    if role not in ("admin","editor","viewer"): role = "viewer"
    if not un or len(pw) < 5:
        flash("Login kiriting va parol kamida 5 belgidan iborat bo'lsin.")
        return redirect(url_for("users_page"))
    conn = db(); c = conn.cursor()
    try:
        c.execute("INSERT INTO users(username, pw_hash, role, full_name) VALUES(?,?,?,?)",
                  (un, generate_password_hash(pw), role, fn))
        conn.commit(); flash(f"'{un}' foydalanuvchisi qo'shildi.")
    except sqlite3.IntegrityError:
        flash("Bu login band. Boshqa login tanlang.")
    conn.close()
    return redirect(url_for("users_page"))

@app.route("/users/update", methods=["POST"])
@role_required("admin")
def users_update():
    uid = int(request.form.get("id"))
    role = request.form.get("role")
    newpw = request.form.get("password","")
    me = current_user()
    conn = db(); c = conn.cursor()
    if role in ("admin","editor","viewer"):
        # o'zining admin rolini tasodifan olib qo'ymaslik uchun: oxirgi adminni himoya qilamiz
        if uid == me["id"] and role != "admin":
            c.execute("SELECT COUNT(*) AS n FROM users WHERE role='admin'")
            if c.fetchone()["n"] <= 1:
                conn.close(); flash("Yagona adminni pasaytirib bo'lmaydi."); return redirect(url_for("users_page"))
        c.execute("UPDATE users SET role=? WHERE id=?", (role, uid))
    if newpw:
        if len(newpw) < 5:
            conn.close(); flash("Parol kamida 5 belgidan iborat bo'lsin."); return redirect(url_for("users_page"))
        c.execute("UPDATE users SET pw_hash=? WHERE id=?", (generate_password_hash(newpw), uid))
    conn.commit(); conn.close(); flash("Saqlandi.")
    return redirect(url_for("users_page"))

@app.route("/users/delete", methods=["POST"])
@role_required("admin")
def users_delete():
    uid = int(request.form.get("id"))
    me = current_user()
    if uid == me["id"]:
        flash("O'zingizni o'chira olmaysiz."); return redirect(url_for("users_page"))
    conn = db(); c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (uid,))
    conn.commit(); conn.close(); flash("Foydalanuvchi o'chirildi.")
    return redirect(url_for("users_page"))

@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403

# ishga tushirishda bazani tayyorlaymiz
with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
