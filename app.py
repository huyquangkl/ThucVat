\
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# -------------------- App & Config --------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
db_url = os.environ.get("DATABASE_URL", "sqlite:///data.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)  # Heroku old scheme
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# -------------------- Models --------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class Species(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    common_name = db.Column(db.String(200), nullable=False)       # Tên Việt Nam / Tên thường gọi
    scientific_name = db.Column(db.String(200), nullable=False)   # Tên khoa học
    family = db.Column(db.String(120), nullable=False)            # Họ
    genus = db.Column(db.String(120))                             # Chi
    location = db.Column(db.String(255))                          # Vị trí
    status = db.Column(db.String(120))                            # Trạng thái
    description = db.Column(db.Text)                              # Mô tả
    image_path = db.Column(db.String(255))                        # Đường dẫn ảnh (trong uploads/)

# -------------------- Auth --------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_admin():
    username = os.environ.get("ADMIN_USERNAME", "ThucvatBM")
    password = os.environ.get("ADMIN_PASSWORD", "Bachma123")
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

# -------------------- Utils --------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# -------------------- Routes --------------------
@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    field = request.args.get("field", "common_name")
    query = Species.query
    if q:
        like = f"%{q}%"
        if field == "scientific_name":
            query = query.filter(Species.scientific_name.ilike(like))
        elif field == "family":
            query = query.filter(Species.family.ilike(like))
        else:
            query = query.filter(Species.common_name.ilike(like))
    species = query.order_by(Species.common_name.asc()).all()
    return render_template("index.html", species=species)

@app.route("/species/<int:species_id>")
def detail_species(species_id):
    sp = Species.query.get_or_404(species_id)
    return render_template("detail.html", species=sp)

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_species():
    if request.method == "POST":
        sp = Species(
            common_name=request.form.get("common_name", "").strip(),
            scientific_name=request.form.get("scientific_name", "").strip(),
            family=request.form.get("family", "").strip(),
            genus=request.form.get("genus", "").strip(),
            location=request.form.get("location", "").strip(),
            status=request.form.get("status", "").strip(),
            description=request.form.get("description", "").strip(),
        )
        # Image upload
        file = request.files.get("image")
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}")
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)
            sp.image_path = filename
        db.session.add(sp)
        db.session.commit()
        flash("Đã thêm loài mới.")
        return redirect(url_for("index"))
    return render_template("form.html", species=None)

@app.route("/edit/<int:species_id>", methods=["GET", "POST"])
@login_required
def edit_species(species_id):
    sp = Species.query.get_or_404(species_id)
    if request.method == "POST":
        sp.common_name = request.form.get("common_name", sp.common_name).strip()
        sp.scientific_name = request.form.get("scientific_name", sp.scientific_name).strip()
        sp.family = request.form.get("family", sp.family).strip()
        sp.genus = request.form.get("genus", sp.genus).strip()
        sp.location = request.form.get("location", sp.location).strip()
        sp.status = request.form.get("status", sp.status).strip()
        sp.description = request.form.get("description", sp.description).strip()
        # Image upload (optional)
        file = request.files.get("image")
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}")
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)
            sp.image_path = filename
        db.session.commit()
        flash("Đã cập nhật loài.")
        return redirect(url_for("detail_species", species_id=sp.id))
    return render_template("form.html", species=sp)

@app.route("/delete/<int:species_id>", methods=["POST"])
@login_required
def delete_species(species_id):
    sp = Species.query.get_or_404(species_id)
    db.session.delete(sp)
    db.session.commit()
    flash("Đã xóa loài.")
    return redirect(url_for("index"))

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/export.csv")
def export_csv():
    q = request.args.get("q", "").strip()
    field = request.args.get("field", "common_name")
    query = Species.query
    if q:
        like = f"%{q}%"
        if field == "scientific_name":
            query = query.filter(Species.scientific_name.ilike(like))
        elif field == "family":
            query = query.filter(Species.family.ilike(like))
        else:
            query = query.filter(Species.common_name.ilike(like))
    rows = query.order_by(Species.common_name.asc()).all()

    def generate():
        header = ["Tên thường gọi", "Tên khoa học", "Họ", "Chi", "Vị trí", "Trạng thái", "Mô tả", "Ảnh"]
        yield ",".join(header) + "\\n"
        for sp in rows:
            values = [
                sp.common_name or "",
                sp.scientific_name or "",
                sp.family or "",
                sp.genus or "",
                sp.location or "",
                sp.status or "",
                (sp.description or "").replace("\\n", " ").replace("\\r", " "),
                sp.image_path or "",
            ]
            out = []
            for v in values:
                if any(c in v for c in [",", "\"", "\\n"]):
                    v = '"' + v.replace('"', '""') + '"'
                out.append(v)
            yield ",".join(out) + "\\n"

    return Response(generate(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=danh_sach_loai.csv"})

# -------------------- Auth Routes --------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Đăng nhập thành công.")
            return redirect(url_for("index"))
        else:
            flash("Sai thông tin đăng nhập.")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Đã đăng xuất.")
    return redirect(url_for("index"))

# -------------------- Init DB immediately (Flask 3 compatible) --------------------
with app.app_context():
    db.create_all()
    init_admin()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
