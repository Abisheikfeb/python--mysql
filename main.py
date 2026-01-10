from flask import Flask, request, redirect, render_template_string, flash
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"

# MySQL config from environment variables
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

# ------------------ HTML TEMPLATE ------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Student Management</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
:root {
    --primary: #2563eb;
    --secondary: #4f46e5;
    --success: #16a34a;
    --danger: #dc2626;
    --bg: #f1f5f9;
    --card: #ffffff;
    --text: #1e293b;
}

* { box-sizing: border-box; }

body {
    margin: 0;
    font-family: 'Segoe UI', system-ui;
    background: var(--bg);
    color: var(--text);
}

.container {
    max-width: 1200px;
    margin: auto;
    padding: 20px;
}

h1 {
    text-align: center;
    margin-bottom: 20px;
    color: var(--secondary);
}

.card {
    background: var(--card);
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 10px 25px rgba(0,0,0,.08);
    margin-bottom: 20px;
}

.form-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
}

input {
    padding: 12px;
    border-radius: 8px;
    border: 1px solid #cbd5e1;
    font-size: 14px;
}

button {
    background: var(--primary);
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
}

button:hover { background: var(--secondary); }

table {
    width: 100%;
    border-collapse: collapse;
}

th {
    background: var(--primary);
    color: white;
    padding: 12px;
}

td {
    padding: 12px;
    border-bottom: 1px solid #e2e8f0;
    text-align: center;
}

.actions {
    display: flex;
    gap: 8px;
    justify-content: center;
}

.actions a {
    padding: 6px 12px;
    border-radius: 6px;
    text-decoration: none;
    font-size: 13px;
    font-weight: 600;
}

.edit {
    background: #e0e7ff;
    color: #3730a3;
}

.delete {
    background: #fee2e2;
    color: #991b1b;
}

.alert {
    padding: 14px;
    border-radius: 10px;
    margin-bottom: 15px;
    font-weight: 600;
}

.success { background: #dcfce7; color: var(--success); }
.danger { background: #fee2e2; color: var(--danger); }

@media (max-width: 900px) {
    .form-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 500px) {
    .form-grid { grid-template-columns: 1fr; }
}
</style>
</head>

<body>
<div class="container">
<h1>🎓 Student Management</h1>

{% with messages = get_flashed_messages(with_categories=true) %}
{% for cat, msg in messages %}
<div class="alert {{cat}}">{{msg}}</div>
{% endfor %}
{% endwith %}

<div class="card">
<form method="POST" action="/add_or_update">
<input type="hidden" name="id" value="{{ student.id if student else '' }}">
<div class="form-grid">
<input name="name" placeholder="Name" value="{{ student.name if student else '' }}" required>
<input name="email" placeholder="Email" value="{{ student.email if student else '' }}" required>
<input name="phone" placeholder="Phone" value="{{ student.phone if student else '' }}" required>
<input name="mark" placeholder="Mark" value="{{ student.mark if student else '' }}" required>
</div>
<br>
<button>{{ 'Update Student' if student else 'Add Student' }}</button>
</form>
</div>

<div class="card">
<table>
<tr>
<th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Mark</th><th>Actions</th>
</tr>

{% for s in students %}
<tr>
<td>{{s[0]}}</td>
<td>{{s[1]}}</td>
<td>{{s[2]}}</td>
<td>{{s[3]}}</td>
<td>{{s[4]}}</td>
<td class="actions">
<a class="edit" href="/edit/{{s[0]}}">Edit</a>
<a class="delete" href="/delete/{{s[0]}}">Delete</a>
</td>
</tr>
{% endfor %}
</table>
</div>

</div>
</body>
</html>
"""

# ------------------ DATABASE FUNCTIONS ------------------
def get_connection():
    return mysql.connector.connect(**db_config, connection_timeout=10)

def get_all_students():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students ORDER BY id")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def get_student(student_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM students WHERE id=%s", (student_id,))
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data

def insert_student(name, email, phone, mark):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO students (name, email, phone, mark) VALUES (%s,%s,%s,%s)",
        (name, email, phone, mark)
    )
    conn.commit()
    cur.close()
    conn.close()

def update_student(id, name, email, phone, mark):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE students SET name=%s, email=%s, phone=%s, mark=%s WHERE id=%s",
        (name, email, phone, mark, id)
    )
    conn.commit()
    cur.close()
    conn.close()

def delete_student(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()


@app.route("/")
def home():
    return render_template_string(
        HTML_TEMPLATE,
        students=get_all_students(),
        student=None
    )

@app.route("/add_or_update", methods=["POST"])
def add_or_update():
    id = request.form.get("id")
    if id:
        update_student(
            id,
            request.form["name"],
            request.form["email"],
            request.form["phone"],
            request.form["mark"]
        )
        flash("Student updated successfully ✅", "success")
    else:
        insert_student(
            request.form["name"],
            request.form["email"],
            request.form["phone"],
            request.form["mark"]
        )
        flash("Student added successfully 🎉", "success")
    return redirect("/")

@app.route("/edit/<int:id>")
def edit(id):
    return render_template_string(
        HTML_TEMPLATE,
        students=get_all_students(),
        student=get_student(id)
    )

@app.route("/delete/<int:id>")
def delete(id):
    delete_student(id)
    flash("Student deleted successfully 🗑️", "danger")
    return redirect("/")

# ------------------ RUN ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
