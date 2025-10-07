
import os
import time
import smtplib
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import pymysql



# Load .env
load_dotenv()

# Basic config from env
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "photo_portfolio")
DB_PORT = os.getenv("DB_PORT", "3306")
FLASK_SECRET = os.getenv("FLASK_SECRET", "change_this_secret")
DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# App factory-ish single-module app
app = Flask(__name__, static_folder="static", template_folder="Templates")
app.jinja_env.globals['datetime'] = datetime
app.secret_key = FLASK_SECRET
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = DEBUG

db = SQLAlchemy(app)



# ---------- Models ----------
class Photographer(db.Model):
    __tablename__ = "photographers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Shot(db.Model):
    __tablename__ = "shots"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=True)
    filename = db.Column(db.String(255), nullable=False)  # store filename only
    caption = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ScheduleRequest(db.Model):
    __tablename__ = "schedule_requests"
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), nullable=False)
    preferred_date = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------- Helpers ----------
def wait_for_mysql(host: str, port: int = 3306, user: str = "root", password: str = "", dbname: str = None, retries: int = 12, delay: int = 2):
    """Wait for MySQL to be reachable before creating tables. Retries with delay."""
    attempt = 0
    while attempt < retries:
        try:
            conn = pymysql.connect(host=host, port=int(port), user=user, password=password, database=dbname, connect_timeout=5)
            conn.close()
            app.logger.info("MySQL is reachable.")
            return True
        except Exception as e:
            attempt += 1
            app.logger.warning(f"MySQL not ready (attempt {attempt}/{retries}): {e}")
            time.sleep(delay)
    raise RuntimeError("Could not connect to MySQL after multiple attempts.")


# ---------- Routes ----------
@app.route("/")
def index():
    photographer = Photographer.query.order_by(Photographer.id).first()
    shots = Shot.query.order_by(Shot.created_at.desc()).limit(6).all()
    return render_template("index.html", photographer=photographer, shots=shots, datetime=datetime)


@app.route("/contact", methods=["POST"])
def contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()
    if not (name and email and message):
        flash("Please fill in all contact fields.", "danger")
        return redirect(url_for("index"))
    cm = ContactMessage(name=name, email=email, message=message)
    db.session.add(cm)
    db.session.commit()
    flash("Message received. Thank you — I will get back to you.", "success")
    return redirect(url_for("index"))


@app.route("/schedule", methods=["POST"])
def schedule():
    client_name = request.form.get("client_name", "").strip()
    email = request.form.get("email", "").strip()
    preferred_date = request.form.get("preferred_date", "").strip()
    notes = request.form.get("notes", "").strip()
    if not (client_name and email):
        flash("Please provide name and email to schedule.", "danger")
        return redirect(url_for("index"))
    req = ScheduleRequest(
        client_name=client_name,
        email=email,
        preferred_date=preferred_date,
        notes=notes,
    )
    db.session.add(req)
    db.session.commit()
    flash("Schedule request sent. I will confirm ASAP.", "success")
    return redirect(url_for("index"))


@app.route("/api/shots")
def api_shots():
    shots = Shot.query.order_by(Shot.created_at.desc()).all()
    data = [{"id": s.id, "title": s.title, "filename": s.filename, "caption": s.caption} for s in shots]
    return jsonify(data)

@app.route('/schedule', methods=['POST'])
def schedule():
    client_name = request.form.get('client_name')
    email = request.form.get('email')
    preferred_date = request.form.get('preferred_date')
    notes = request.form.get('notes')

    message = f"""Subject: New Shoot Request

    Client: {client_name}
    Email: {email}
    Preferred Date: {preferred_date}
    Notes: {notes}
    """

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('adityagaikwad6430@gmail.com', 'ygql wvot xnux qjuz')
        smtp.sendmail('adityagaikwad6430@gmail.com', 'yg700900@gmail.com', message)

    return "Request sent via Email!"


# ---------- DB init on startup (automated but safe) ----------
def ensure_db_ready_and_migrate():
    # Wait for DB to be reachable (works in Docker Compose where host=db)
    wait_for_mysql(host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASS, dbname=DB_NAME, retries=20, delay=2)

    # Create tables if they do not exist
    with app.app_context():
        db.create_all()
        app.logger.info("Ensured database tables exist.")


# Run the DB readiness check only when imported/run by server process (not during unit tests unless desired)
try:
    # Only attempt DB readiness when not in test environment
    if __name__ != "pytest":
        ensure_db_ready_and_migrate()
except Exception as e:
    # If DB can't be reached, fail fast so container logs show why
    app.logger.exception("Database initialization failed: %s", e)
    # Re-raise to stop the process (so Docker restarts according to restart policy)
    raise


if __name__ == "__main__":
    # Local dev fallback; in production you'll use Gunicorn (configured in Dockerfile)
    app.run(debug=DEBUG, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

