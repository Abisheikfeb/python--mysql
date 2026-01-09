from flask import Flask, request, redirect, render_template_string
import mysql.connector
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

db_config = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME")
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Student Management</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>
        
        @media (max-width: 576px) {
            h1 {
                font-size: 22px;
            }

            .container {
                padding: 10px;
            }

            table {
                font-size: 12px;
            }

            .btn {
                width: 100%;
                margin-bottom: 5px;
            }

            .table-responsive {
                overflow-x: auto;
            }
        }

        
        @media (min-width: 577px) and (max-width: 991px) {
            h1 {
                font-size: 26px;
            }

            table {
                font-size: 14px;
            }
        }

        
        @media (min-width: 992px) {
            h1 {
                font-size: 32px;
            }
        }
    </style>
</head>

<body class="bg-light">
<div class="container mt-5">
    <h1 class="text-center mb-4">Student Management</h1>

    <div class="card shadow mb-4">
        <div class="card-body">
            <form method="POST" action="{{ url_for('add_or_update') }}">
                <input type="hidden" name="id" value="{{ student.id if student else '' }}">

                <div class="mb-3">
                    <input type="text" name="name" class="form-control" placeholder="Name" required value="{{ student.name if student else '' }}">
                </div>

                <div class="mb-3">
                    <input type="email" name="email" class="form-control" placeholder="Email" required value="{{ student.email if student else '' }}">
                </div>

                <div class="mb-3">
                    <input type="text" name="phone" class="form-control" placeholder="Phone" required value="{{ student.phone if student else '' }}">
                </div>

                <div class="mb-3">
                    <input type="number" name="mark" class="form-control" placeholder="Mark" required value="{{ student.mark if student else '' }}">
                </div>

                <button class="btn btn-primary">
                    {{ 'Update Student' if student else 'Add Student' }}
                </button>

                {% if student %}
                <a href="/" class="btn btn-secondary mt-2">Cancel</a>
                {% endif %}
            </form>
        </div>
    </div>

    <h2 class="text-center mb-3">All Students</h2>

    <div class="table-responsive">
        <table class="table table-striped table-hover">
            <thead class="table-dark">
                <tr>
                    <th>ID</th><th>Name</th><th>Email</th>
                    <th>Phone</th><th>Mark</th><th>Action</th>
                </tr>
            </thead>
            <tbody>
                {% for s in students %}
                <tr>
                    <td>{{ s[0] }}</td>
                    <td>{{ s[1] }}</td>
                    <td>{{ s[2] }}</td>
                    <td>{{ s[3] }}</td>
                    <td>{{ s[4] }}</td>
                    <td>
                        <a href="/edit/{{ s[0] }}" class="btn btn-sm btn-warning">Edit</a>
                        <a href="/delete/{{ s[0] }}" class="btn btn-sm btn-danger"
                           onclick="return confirm('Are you sure?')">Delete</a>
                    </td>
                </tr>
                {% endfor %}
                {% if not students %}
                <tr>
                    <td colspan="6" class="text-center text-muted">No students found</td>
                </tr>
                {% endif %}
            </tbody>
        </table>
    </div>
</div>
</body>
</html>
"""




def get_connection():
    return mysql.connector.connect(**db_config)

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100),
            phone VARCHAR(15),
            mark INT
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

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
    cursor.execute(
        "INSERT INTO students (name, email, phone, mark) VALUES (%s, %s, %s, %s)",
        (name, email, phone, mark)
    )
    conn.commit()
    cursor.close()
    conn.close()

def update_student(id, name, email, phone, mark):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE students SET name=%s, email=%s, phone=%s, mark=%s WHERE id=%s",
        (name, email, phone, mark, id)
    )
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



@app.route('/')
def home():
    create_table()
    return render_template_string(HTML_TEMPLATE, students=get_all_students(), student=None)

@app.route('/add_or_update', methods=['POST'])
def add_or_update():
    id = request.form.get('id')
    if id:
        update_student(id, request.form['name'], request.form['email'],
                       request.form['phone'], request.form['mark'])
    else:
        insert_student(request.form['name'], request.form['email'],
                       request.form['phone'], request.form['mark'])
    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):
    return render_template_string(
        HTML_TEMPLATE,
        students=get_all_students(),
        student=get_student(id)
    )

@app.route('/delete/<int:id>')
def delete(id):
    delete_student(id)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
