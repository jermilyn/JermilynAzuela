from flask import Flask, jsonify, request, render_template_string
import sqlite3

app = Flask(__name__)

# ==============================
# DATABASE CONNECTION
# ==============================
def get_db():
    conn = sqlite3.connect("students_reg.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    # Updated table to include student_id and age
    conn.execute("""
    CREATE TABLE IF NOT EXISTS student (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE,
        name TEXT,
        age INTEGER,
        section TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ==============================
# UI DESIGN (REGISTRATION FORM)
# ==============================
html_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Registration</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f4f7f6; display: flex; flex-direction: column; align-items: center; padding: 40px; }
        .card { background: white; width: 450px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); overflow: hidden; margin-bottom: 30px; }
        .header { background: #5842e3; color: white; padding: 25px; text-align: center; }
        .header h2 { margin: 0; font-size: 24px; }
        
        .content { padding: 25px; }
        label { display: block; font-weight: bold; margin: 10px 0 5px; color: #333; font-size: 14px; }
        input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; font-size: 16px; margin-bottom: 5px; }
        
        .btn-register { 
            width: 100%; background: #5842e3; color: white; border: none; padding: 15px; 
            border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 20px;
            transition: 0.2s;
        }
        .btn-register:hover { background: #4532b5; }
        
        #message { text-align: center; font-weight: bold; margin-top: 15px; min-height: 20px; }

        /* Registered Students Table */
        .list-container { width: 100%; max-width: 700px; background: white; border-radius: 12px; padding: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #eee; }
        th { color: #5842e3; border-bottom: 2px solid #5842e3; }
    </style>
</head>
<body>

<div class="card">
    <div class="header">
        <h2>Student Registration</h2>
        <p>Enter details to add to database</p>
    </div>

    <div class="content">
        <label>Student ID</label>
        <input type="text" id="student_id" placeholder="e.g. 2024-001">

        <label>Full Name</label>
        <input type="text" id="name" placeholder="Enter full name">

        <label>Age</label>
        <input type="number" id="age" placeholder="Enter age">

        <label>Section</label>
        <input type="text" id="section" placeholder="Enter section">

        <button type="button" id="regBtn" class="btn-register" onclick="registerStudent()">Register Student</button>
        <p id="message"></p>
    </div>
</div>

<div class="list-container">
    <h3>Registered Students</h3>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Age</th>
                <th>Section</th>
            </tr>
        </thead>
        <tbody id="studentTableBody">
            </tbody>
    </table>
</div>

<script>
    function showMessage(msg, color) {
        const m = document.getElementById("message");
        m.innerText = msg;
        m.style.color = color === "green" ? "#2ecc71" : "#e74c3c";
        setTimeout(() => { m.innerText = ""; }, 3000);
    }

    function loadStudents() {
        fetch('/students_list').then(r => r.json()).then(data => {
            const tbody = document.getElementById("studentTableBody");
            tbody.innerHTML = "";
            data.forEach(s => {
                tbody.innerHTML += `
                    <tr>
                        <td>${s.student_id}</td>
                        <td>${s.name}</td>
                        <td>${s.age}</td>
                        <td>${s.section}</td>
                    </tr>
                `;
            });
        });
    }

    function registerStudent() {
        const student_id = document.getElementById("student_id").value;
        const name = document.getElementById("name").value;
        const age = document.getElementById("age").value;
        const section = document.getElementById("section").value;
        const btn = document.getElementById("regBtn");

        if(!student_id || !name || !age || !section) {
            showMessage("Please fill in all fields", "red");
            return;
        }

        btn.innerText = "Registering...";
        btn.disabled = true;

        fetch('/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                student_id: student_id,
                name: name,
                age: age,
                section: section
            })
        })
        .then(r => r.json())
        .then(data => {
            if(data.status === "success") {
                showMessage("Registration successful!", "green");
                // Clear fields
                document.getElementById("student_id").value = "";
                document.getElementById("name").value = "";
                document.getElementById("age").value = "";
                document.getElementById("section").value = "";
                loadStudents(); // Refresh table
            } else {
                showMessage("Error: " + data.message, "red");
            }
        })
        .finally(() => {
            btn.innerText = "Register Student";
            btn.disabled = false;
        });
    }

    // Initial load
    loadStudents();
</script>

</body>
</html>
"""

# ==============================
# ROUTES
# ==============================
@app.route('/')
def home():
    return render_template_string(html_page)

@app.route('/students_list')
def list_students():
    conn = get_db()
    rows = conn.execute("SELECT * FROM student ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO student (student_id, name, age, section) VALUES (?, ?, ?, ?)", 
            (data['student_id'], data['name'], data['age'], data['section'])
        )
        conn.commit()
        return jsonify({"status": "success"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Student ID already exists"})
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)
