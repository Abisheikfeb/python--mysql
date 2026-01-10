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
    <title>Student Database Pro</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #4f46e5;
            --email-clr: #0ea5e9;
            --phone-clr: #10b981;
            --mark-clr: #8b5cf6;
            --bg: #f1f5f9;
            --live-green: #22c55e;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #eef2f3; padding: 10px; }
        
        /* 1. HEADER FIX FOR MOBILE */
        .header-section {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 5px;
            margin-bottom: 10px;
        }

        .main-title { font-size: 22px; color: #1e293b; display: flex; align-items: center; gap: 8px; }

        /* 2. LIVE STATUS FIXED */
        .live-status {
            display: flex;
            align-items: center;
            gap: 8px;
            background: #ffffff;
            padding: 6px 12px;
            border-radius: 50px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid #e2e8f0;
        }

        .pulse-dot {
            width: 10px;
            height: 10px;
            background: var(--live-green);
            border-radius: 50%;
            position: relative;
        }

        .pulse-dot::after {
            content: "";
            position: absolute;
            width: 100%;
            height: 100%;
            background: var(--live-green);
            border-radius: 50%;
            animation: pulse-ring 1.5s cubic-bezier(0.455, 0.03, 0.515, 0.955) infinite;
        }

        @keyframes pulse-ring {
            0% { transform: scale(0.33); opacity: 1; }
            80%, 100% { transform: scale(2.5); opacity: 0; }
        }

        .mini-graph { display: flex; align-items: flex-end; gap: 2px; height: 12px; }
        .bar { width: 3px; background: var(--live-green); border-radius: 1px; animation: grow 1s infinite alternate; }
        @keyframes grow { from { height: 3px; } to { height: 12px; } }

        .status-text { font-size: 10px; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }

        /* 3. INPUT CARD */
        .input-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); margin-bottom: 25px; border-top: 5px solid var(--primary); }
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; }
        input { width: 100%; padding: 12px; border: 2px solid #e2e8f0; border-radius: 8px; outline: none; transition: 0.3s; font-size: 16px; }
        input:focus { border-color: var(--primary); }

        .btn-save { 
            background: var(--primary); color: white; border: none; border-radius: 8px; 
            font-weight: bold; cursor: pointer; padding: 12px; transition: all 0.3s;
            display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 15px;
        }
        .btn-save.loading { background: #6366f1; opacity: 0.8; }
        .btn-save.success { background: var(--live-green); }

        /* 4. STUDENT BOXES */
        .student-list { display: grid; grid-template-columns: 1fr; gap: 15px; }
        .student-box { background: white; border-radius: 15px; padding: 18px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 6px solid var(--primary); }
        .val-name { font-size: 17px; font-weight: 800; color: #1e293b; margin-bottom: 10px; border-bottom: 1px solid #f1f5f9; padding-bottom: 5px; display: block; }
        .data-row { display: flex; align-items: center; margin-bottom: 6px; gap: 10px; }
        .label { font-weight: bold; font-size: 10px; color: #94a3b8; text-transform: uppercase; width: 50px; }
        .val-email { color: var(--email-clr); font-weight: 600; word-break: break-all; font-size: 13px; }
        .val-phone { color: var(--phone-clr); font-weight: 600; font-size: 13px; }
        .val-mark { background: #f3e8ff; color: var(--mark-clr); padding: 2px 10px; border-radius: 20px; font-weight: bold; font-size: 13px;}

        .actions { margin-top: 15px; display: flex; gap: 8px; }
        .action-btn { flex: 1; padding: 10px; text-align: center; border-radius: 8px; text-decoration: none; font-size: 13px; font-weight: bold; }
        .edit-btn { background: #fff7ed; color: #f59e0b; border: 1px solid #fed7aa; }
        .del-btn { background: #fef2f2; color: #ef4444; border: 1px solid #fee2e2; }

        @media (min-width: 768px) {
            .student-list { grid-template-columns: 1fr 1fr; }
            .main-title { font-size: 28px; }
        }
    </style>
</head>
<body>

    <div class="container" style="max-width: 900px; margin: 0 auto;">
        <div class="header-section">
            <h1 class="main-title"><i class="fas fa-server"></i> Portal</h1>
            <div class="live-status">
                <div class="mini-graph">
                    <div class="bar"></div>
                    <div class="bar" style="animation-delay: 0.2s;"></div>
                    <div class="bar" style="animation-delay: 0.4s;"></div>
                </div>
                <span class="status-text">Live</span>
                <div class="pulse-dot"></div>
            </div>
        </div>

        <div class="input-card">
            <form id="studentForm" action="/add_or_update" method="POST" class="form-grid">
                <input type="hidden" name="id" value="{{ student.id if student else '' }}">
                <input type="text" name="name" placeholder="Name" value="{{ student.name if student else '' }}" required>
                <input type="email" name="email" placeholder="Email" value="{{ student.email if student else '' }}" required>
                <input type="text" name="phone" placeholder="Phone" value="{{ student.phone if student else '' }}" required>
                <input type="number" name="mark" placeholder="Marks" value="{{ student.mark if student else '' }}" required>
                <button type="submit" id="submitBtn" class="btn-save">
                    <i class="fas fa-plus-circle"></i> 
                    <span id="btnText">{{ 'Update' if student else 'Add Student' }}</span>
                </button>
            </form>
        </div>

        <div class="student-list">
            {% for s in students %}
            <div class="student-box">
                <span class="val-name"><i class="fas fa-id-card"></i> {{ s[1] }}</span>
                <div class="data-row"><span class="label">Email</span><span class="val-email">{{ s[2] }}</span></div>
                <div class="data-row"><span class="label">Phone</span><span class="val-phone">{{ s[3] }}</span></div>
                <div class="data-row"><span class="label">Score</span><span class="val-mark">{{ s[4] }}</span></div>
                <div class="actions">
                    <a href="/edit/{{ s[0] }}" class="action-btn edit-btn">Edit</a>
                    <a href="/delete/{{ s[0] }}" class="action-btn del-btn" onclick="return confirm('Delete?')">Delete</a>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        const form = document.getElementById('studentForm');
        const btn = document.getElementById('submitBtn');
        const btnText = document.getElementById('btnText');

        form.onsubmit = function() {
            btn.classList.add('loading');
            btnText.innerHTML = '<i class="fas fa-plug"></i> Connecting...';
            setTimeout(() => { btnText.innerHTML = '<i class="fas fa-hourglass-half"></i> Processing...'; }, 700);
            setTimeout(() => {
                btn.classList.remove('loading');
                btn.classList.add('success');
                btnText.innerHTML = '<i class="fas fa-check-circle"></i> Success!';
            }, 1400);
            setTimeout(() => { form.submit(); }, 1800);
            return false;
        };
    </script>
</body>
</html>
"""

# (KEEP ALL PREVIOUS DATABASE LOGIC AND ROUTES EXACTLY THE SAME)
def get_connection():
    return mysql.connector.connect(**db_config, connection_timeout=10)

def get_all_students():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT * FROM students ORDER BY id DESC")
    data = cur.fetchall(); cur.close(); conn.close()
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