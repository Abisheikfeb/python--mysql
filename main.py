from flask import Flask, request, redirect, render_template_string, flash
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"

db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Registry 2026</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #f0f4f8; color: #334155; padding: 15px; }
        
        .container { max-width: 1000px; margin: 0 auto; }
        
        .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 25px; }
        
        /* Form grid - responsive */
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }
        input { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 15px; }
        
        .btn { padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; text-decoration: none; display: inline-block; text-align: center; }
        .btn-primary { background: #2563eb; color: white; width: 100%; }
        .btn-edit { background: #f59e0b; color: white; font-size: 13px; }
        .btn-delete { background: #ef4444; color: white; font-size: 13px; }

        /* Table & Text Wrap Fix */
        table { width: 100%; border-collapse: collapse; background: white; border-radius: 12px; table-layout: fixed; }
        th { background: #1e293b; color: white; padding: 12px; text-align: left; font-size: 14px; }
        
        td { 
            padding: 12px; 
            border-bottom: 1px solid #e2e8f0; 
            font-size: 14px;
            /* Fix long emails/text */
            word-wrap: break-word;
            overflow-wrap: break-word;
            word-break: break-all;
            white-space: normal;
        }

        /* MOBILE VIEW */
        @media screen and (max-width: 768px) {
            thead { display: none; }
            table, tbody, tr, td { display: block; width: 100%; }
            tr { margin-bottom: 15px; border: 1px solid #e2e8f0; border-radius: 12px; padding: 10px; background: #fff; }
            
            td { 
                text-align: right; 
                padding-left: 40%; 
                position: relative; 
                border-bottom: 1px solid #f1f5f9; 
                min-height: 40px;
            }
            
            td::before {
                content: attr(data-label);
                position: absolute; left: 10px; width: 35%; text-align: left;
                font-weight: bold; color: #64748b;
            }
            
            .btn-edit, .btn-delete { width: 48%; margin-top: 5px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h2 style="margin: 20px 0; text-align: center;">Student Management</h2>

        <div class="card">
            <form action="/add_or_update" method="POST" class="form-grid">
                <input type="hidden" name="id" value="{{ student.id if student else '' }}">
                <input type="text" name="name" placeholder="Name" value="{{ student.name if student else '' }}" required>
                <input type="email" name="email" placeholder="Email" value="{{ student.email if student else '' }}" required>
                <input type="text" name="phone" placeholder="Phone" value="{{ student.phone if student else '' }}" required>
                <input type="number" name="mark" placeholder="Mark" value="{{ student.mark if student else '' }}" required>
                <button type="submit" class="btn btn-primary">{{ 'Update' if student else 'Add Student' }}</button>
            </form>
        </div>

        <table>
            <thead>
                <tr>
                    <th style="width: 25%;">Name</th>
                    <th style="width: 30%;">Email</th>
                    <th style="width: 20%;">Phone</th>
                    <th style="width: 10%;">Mark</th>
                    <th style="width: 15%;">Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for s in students %}
                <tr>
                    <td data-label="Name">{{ s[1] }}</td>
                    <td data-label="Email">{{ s[2] }}</td>
                    <td data-label="Phone">{{ s[3] }}</td>
                    <td data-label="Mark">{{ s[4] }}</td>
                    <td data-label="Actions">
                        <a href="/edit/{{ s[0] }}" class="btn btn-edit">Edit</a>
                        <a href="/delete/{{ s[0] }}" class="btn btn-delete" onclick="return confirm('Delete?')">X</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

# --- DATABASE LOGIC (Same as your previous) ---
def get_connection():
    return mysql.connector.connect(**db_config, connection_timeout=10)

def get_all_students():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students ORDER BY id DESC")
    data = cur.fetchall()
    cur.close(); conn.close()
    return data

def get_student(student_id):
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM students WHERE id=%s", (student_id,))
    data = cur.fetchone(); cur.close(); conn.close()
    return data

def insert_student(name, email, phone, mark):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO students (name, email, phone, mark) VALUES (%s,%s,%s,%s)", (name, email, phone, mark))
    conn.commit(); cur.close(); conn.close()

def update_student(id, name, email, phone, mark):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("UPDATE students SET name=%s, email=%s, phone=%s, mark=%s WHERE id=%s", (name, email, phone, mark, id))
    conn.commit(); cur.close(); conn.close()

def delete_student(id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id,))
    conn.commit(); cur.close(); conn.close()

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE, students=get_all_students(), student=None)

@app.route("/add_or_update", methods=["POST"])
def add_or_update():
    sid = request.form.get("id")
    if sid:
        update_student(sid, request.form["name"], request.form["email"], request.form["phone"], request.form["mark"])
    else:
        insert_student(request.form["name"], request.form["email"], request.form["phone"], request.form["mark"])
    return redirect("/")

@app.route("/edit/<int:id>")
def edit(id):
    return render_template_string(HTML_TEMPLATE, students=get_all_students(), student=get_student(id))

@app.route("/delete/<int:id>")
def delete(id):
    delete_student(id)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)