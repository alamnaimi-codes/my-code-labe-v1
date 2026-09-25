from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")


# ================= DATABASE =================

def get_db():
    db_path = app.config.get("DATABASE", DATABASE)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    # Questions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            question TEXT NOT NULL,
            language TEXT NOT NULL
        )
    """)

    # Notes table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            note TEXT NOT NULL
        )
    """)

    # Code files table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS code_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            language TEXT NOT NULL,
            code TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def clean_input(value):
    if value is None:
        return ""
    return str(value).strip()


# ================= DASHBOARD =================

@app.route("/")
def home():

    conn = get_db()

    questions = conn.execute(
        "SELECT * FROM questions ORDER BY id DESC"
    ).fetchall()

    notes = conn.execute(
        "SELECT * FROM notes ORDER BY id DESC"
    ).fetchall()

    code_files = conn.execute(
        "SELECT * FROM code_files ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        questions=questions,
        notes=notes,
        code_files=code_files
    )


# ================= ADD QUESTION =================

@app.route("/add-question", methods=["POST"])
def add_question():

    title = clean_input(request.form.get("title", ""))
    question = clean_input(request.form.get("question", ""))
    language = clean_input(request.form.get("language", ""))

    if not title or not question or not language:
        return redirect(url_for("home"))

    conn = get_db()

    conn.execute(
        """
        INSERT INTO questions (title, question, language)
        VALUES (?, ?, ?)
        """,
        (title, question, language)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


@app.route("/edit-question/<int:question_id>")
def edit_question(question_id):
    conn = get_db()
    question = conn.execute(
        "SELECT * FROM questions WHERE id = ?",
        (question_id,)
    ).fetchone()
    conn.close()

    if question is None:
        return redirect(url_for("home"))

    return render_template("edit_question.html", question=question)


@app.route("/update-question/<int:question_id>", methods=["POST"])
def update_question(question_id):
    title = clean_input(request.form.get("title", ""))
    question = clean_input(request.form.get("question", ""))
    language = clean_input(request.form.get("language", ""))

    if not title or not question or not language:
        return redirect(url_for("home"))

    conn = get_db()
    conn.execute(
        """
        UPDATE questions
        SET title = ?, question = ?, language = ?
        WHERE id = ?
        """,
        (title, question, language, question_id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("home"))


# ================= ADD NOTE =================

@app.route("/add-note", methods=["POST"])
def add_note():

    title = clean_input(request.form.get("title", ""))
    note = clean_input(request.form.get("note", ""))

    if not title or not note:
        return redirect(url_for("home"))

    conn = get_db()

    conn.execute(
        """
        INSERT INTO notes (title, note)
        VALUES (?, ?)
        """,
        (title, note)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


@app.route("/edit-note/<int:note_id>")
def edit_note(note_id):
    conn = get_db()
    note = conn.execute(
        "SELECT * FROM notes WHERE id = ?",
        (note_id,)
    ).fetchone()
    conn.close()

    if note is None:
        return redirect(url_for("home"))

    return render_template("edit_note.html", note=note)


@app.route("/update-note/<int:note_id>", methods=["POST"])
def update_note(note_id):
    title = clean_input(request.form.get("title", ""))
    note = clean_input(request.form.get("note", ""))

    if not title or not note:
        return redirect(url_for("home"))

    conn = get_db()
    conn.execute(
        """
        UPDATE notes
        SET title = ?, note = ?
        WHERE id = ?
        """,
        (title, note, note_id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("home"))


# ================= CODE EDITOR =================

@app.route("/editor")
def editor():

    conn = get_db()

    code_files = conn.execute(
        "SELECT * FROM code_files ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "editor.html",
        code_files=code_files
    )


# ================= SAVE CODE =================

@app.route("/save-code", methods=["POST"])
def save_code():

    filename = clean_input(request.form.get("filename", ""))
    language = clean_input(request.form.get("language", ""))
    code = clean_input(request.form.get("code", ""))

    if not filename or not language or not code:
        return redirect(url_for("editor"))

    conn = get_db()

    conn.execute(
        """
        INSERT INTO code_files (filename, language, code)
        VALUES (?, ?, ?)
        """,
        (filename, language, code)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("editor"))


@app.route("/edit-code/<int:code_id>")
def edit_code(code_id):
    conn = get_db()
    code_file = conn.execute(
        "SELECT * FROM code_files WHERE id = ?",
        (code_id,)
    ).fetchone()
    conn.close()

    if code_file is None:
        return redirect(url_for("editor"))

    return render_template("edit_code.html", code_file=code_file)


@app.route("/update-code/<int:code_id>", methods=["POST"])
def update_code(code_id):
    filename = clean_input(request.form.get("filename", ""))
    language = clean_input(request.form.get("language", ""))
    code = clean_input(request.form.get("code", ""))

    if not filename or not language or not code:
        return redirect(url_for("editor"))

    conn = get_db()
    conn.execute(
        """
        UPDATE code_files
        SET filename = ?, language = ?, code = ?
        WHERE id = ?
        """,
        (filename, language, code, code_id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("editor"))


# ================= DELETE QUESTION =================

@app.route("/delete-question/<int:question_id>")
def delete_question(question_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM questions WHERE id = ?",
        (question_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


# ================= DELETE NOTE =================

@app.route("/delete-note/<int:note_id>")
def delete_note(note_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM notes WHERE id = ?",
        (note_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


# ================= DELETE CODE =================

@app.route("/delete-code/<int:code_id>")
def delete_code(code_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM code_files WHERE id = ?",
        (code_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("editor"))


# ================= START =================

if __name__ == "__main__":

    init_db()

    print("================================")
    print("       My CodeLab")
    print("================================")
    print("Open: http://127.0.0.1:8000")

    app.run(
        host="127.0.0.1",
        port=8000,
        debug=False
    )