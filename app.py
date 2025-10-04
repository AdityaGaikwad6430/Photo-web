import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# load env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "change_this_secret")

DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "root" , "")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_NAME = os.getenv("DB_NAME", "photo_portfolio")
DB_PORT = os.getenv("DB_PORT", "3306")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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
    filename = db.Column(db.String(255), nullable=False)  # store path/filename
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

# ---------- Routes ----------
@app.route("/")
def index():
    # For now we take the first photographer and shots
    photographer = Photographer.query.order_by(Photographer.id).first()
    shots = Shot.query.order_by(Shot.created_at.desc()).limit(6).all()
    return render_template("index.html", photographer=photographer, shots=shots)

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
    req = ScheduleRequest(client_name=client_name, email=email,
                          preferred_date=preferred_date, notes=notes)
    db.session.add(req)
    db.session.commit()
    flash("Schedule request sent. I will confirm ASAP.", "success")
    return redirect(url_for("index"))

# Minimal API to fetch shots (useful later)
@app.route("/api/shots")
def api_shots():
    shots = Shot.query.order_by(Shot.created_at.desc()).all()
    data = [{"id": s.id, "title": s.title, "filename": s.filename, "caption": s.caption} for s in shots]
    return jsonify(data)

# Admin helper to init DB (run once)
@app.cli.command("init-db")
def init_db():
    """Create database tables (call: flask init-db)"""
    db.create_all()
    print("Database tables created.")

if __name__ == "__main__":
    app.run(debug=True)
