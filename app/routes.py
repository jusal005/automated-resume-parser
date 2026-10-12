import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.models import db, Candidate
from app.parser import parse_resume

main = Blueprint("main", __name__)
ALLOWED_EXTENSIONS = {"pdf", "docx"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/upload", methods=["POST"])
def upload_file():
    if "resume" not in request.files:
        flash("No file uploaded", "error")
        return redirect(url_for("main.index"))

    file = request.files["resume"]
    if file.filename == "":
        flash("No file selected", "error")
        return redirect(url_for("main.index"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
        file.save(upload_path)

        try:
            parsed_data = parse_resume(upload_path)
            candidate = Candidate(
                name=parsed_data["name"],
                email=parsed_data["email"],
                phone=parsed_data["phone"],
                skills=parsed_data["skills"],
                education=parsed_data["education"],
                raw_text=parsed_data["raw_text"],
                filename=filename
            )
            db.session.add(candidate)
            db.session.commit()
            flash(f"Resume parsed successfully for {candidate.name or 'Candidate'}!", "success")
            return redirect(url_for("main.candidates"))
        except Exception as e:
            flash(f"Error parsing resume: {str(e)}", "error")
            return redirect(url_for("main.index"))

    flash("Allowed file types are PDF and DOCX", "error")
    return redirect(url_for("main.index"))

@main.route("/candidates")
def candidates():
    query = request.args.get("q", "").strip()
    if query:
        search_filter = f"%{query}%"
        candidates_list = Candidate.query.filter(
            (Candidate.name.ilike(search_filter)) |
            (Candidate.skills.ilike(search_filter)) |
            (Candidate.education.ilike(search_filter))
        ).order_by(Candidate.created_at.desc()).all()
    else:
        candidates_list = Candidate.query.order_by(Candidate.created_at.desc()).all()
    return render_template("candidates.html", candidates=candidates_list, query=query)
