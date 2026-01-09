from flask import Flask, request, redirect, render_template_string
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# MySQL config from environment variables
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
    <title>Students Management</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(to right, #ffecd2, #fcb69f);
            margin: 0; padding: 20px;
        }
        h1 { text-align: center; color: #333; }
        table {
            width: 80%; margin: 20px auto; border-collapse: collapse; background-color: #ffffffcc;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        th, td { padding: 12px; text-align: center; border-bottom: 1px solid #ddd; }
        th { background-color: #f57c00; color: white; }
        tr:hover { background-color: #ffe0b2; }
        form {
            width: 80%; margin: 20px auto; background-color: #ffffffcc;
            padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        input[type=text], input[type=number], input[type=email] {
            padding: 10px; margin: 5px; width: 23%; border-radius: 5px; border: 1px solid #ccc;
        }
        input[type=submit] {
            padding: 10px 20px; background-color: #f57c00; color: white;
            border: none; border-radius: 5px; cursor: pointer; margin-top: 10px;
        }
        input[type=submit]:hover { background-color: #ef6c00; }
        a.button {
            text-decoration: none; padding: 5px 10px; background-color: #1976d2;
            color: white; border-radius: 5px; margin: 0 5px;
        }
        a.button:hover { background-color: #0d47a1; }
    </style>
</head>
<body>
    <h1>Students Management</h1>

    <form action="/add_or_update" method="POST">
        <input type="hidden" name="id" value="{{ student.id if student else '' }}">
        <input type="text" name="name" placeholder="Name" value="{{ student.name if student else '' }}" required>
        <input type="email" name="email" placeholder="Email" value="{{ student.email if student else '' }}" required>
        <input type="text" name="phone" placeholder="Phone" value="{{ student.phone if student else '' }}" required>
        <input type="number" name="mark" placeholder="Mark" value="{{ student.mark if student else '' }}" required>
        <input type="submit" value="{{ 'Update' if student else 'Add' }} Student">
    </form>

    <table>
        <tr>
            <th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Mark</th><th>Actions</th>
        </tr>
        {% for s in students %}
        <tr>
            <td>{{ s[0] }}</td><td>{{ s[1] }}</td><td>{{ s[2] }}</td><td>{{ s[3] }}</td><td>{{ s[4] }}</td>
            <td>
                <a class="button" href="/edit/{{ s[0] }}">Edit</a>
                <a class="button" href="/delete/{{ s[0] }}">Delete</a>
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# Database functions
def get_connection():
    return mysql.connector.connect(**db_config, connection_timeout=10)

def get_all_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY id")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def get_student(student_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE id=%s", (student_id,))
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return data

def insert_student(name, email, phone, mark):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, email, phone, mark) VALUES (%s,%s,%s,%s)",
                   (name, email, phone, mark))
    conn.commit()
    cursor.close()
    conn.close()

def update_student(id, name, email, phone, mark):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET name=%s,email=%s,phone=%s,mark=%s WHERE id=%s",
                   (name, email, phone, mark, id))
    conn.commit()
    cursor.close()
    conn.close()

def delete_student(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

# Routes
@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE, students=get_all_students(), student=None)

@app.route("/add_or_update", methods=["POST"])
def add_or_update():
    id = request.form.get("id")
    if id:
        update_student(id, request.form["name"], request.form["email"], request.form["phone"], request.form["mark"])
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

# Run Flask on Clever Cloud dynamic port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
