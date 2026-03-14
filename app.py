from flask import Flask, jsonify, request, render_template_string
import sqlite3

app = Flask(__name__)

# ==============================
# DATABASE CONNECTION & SETUP
# ==============================
def get_db():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        grade INTEGER,
        section TEXT
    )
    """)
    default_students = [
        ("Jermilyn Azuela", 10, "Zechariah"),
        ("Alice Santos", 9, "Genesis"),
        ("Mark Lopez", 11, "Exodus")
    ]
    for s in default_students:
        cursor.execute("INSERT OR IGNORE INTO student (name, grade, section) VALUES (?, ?, ?)", s)
    conn.commit()
    conn.close()

init_db()

# ==============================
# MODERN UI DESIGN (DASHBOARD STYLE)
# ==============================
html_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Manager Pro</title>
    <style>
        :root {
            --primary: #4f46e5;
            --primary-hover: #4338ca;
            --bg: #f8fafc;
            --card: #ffffff;
            --text-main: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
        }

        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }

        .dashboard {
            background: var(--card);
            width: 100%;
            max-width: 500px;
            border-radius: 16px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            border: 1px solid var(--border);
        }

        .header {
            background: var(--primary);
            padding: 24px;
            color: white;
            text-align: center;
        }

        .header h2 { margin: 0; font-size: 1.5rem; letter-spacing: -0.025em; }
        .header p { margin: 4px 0 0; opacity: 0.8; font-size: 0.875rem; }

        .content { padding: 24px; }

        .form-group { margin-bottom: 20px; }
        label { display: block; font-size: 0.875rem; font-weight: 600; margin-bottom: 6px; color: var(--text-main); }

        select, input {
            width: 100%;
            padding: 12px;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.2s;
            box-sizing: border-box;
            background: #fff;
        }

        select:focus, input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }

        .info-card {
            background: #f1f5f9;
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 24px;
            display: none; /* Hidden until selection */
            border: 1px dashed var(--border);
        }

        .info-card div { margin-bottom: 4px; font-size: 0.95rem; }
        .info-card strong { color: var(--primary); }

        .btn-submit {
            width: 100%;
            padding: 14px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }

        .btn-submit:hover { background: var(--primary-hover); }

        #message {
            text-align: center;
            margin-top: 16px;
            font-size: 0.875rem;
            font-weight: 500;
            min-height: 20px;
        }

        .divider {
            height: 1px;
            background: var(--border);
            margin: 24px 0;
        }
    </style>
</head>
<body>

<div class="dashboard">
    <div class="header">
        <h2>Student Information</h2>
        <p>Database Management System</p>
    </div>

    <div class="content">
        <div class="form-group">
            <label>Select Student Profile</label>
            <select id="studentSelect" onchange="loadStudent()">
                <option value="">Choose a student...</option>
            </select>
        </div>

        <div id="studentData" class="info-card"></div>

        <div class="divider"></div>

        <div class="form-group">
            <label>Update Grade</label>
            <input type="number" id="grade" placeholder="Enter new grade (e.g. 11)">
        </div>

        <div class="form-group">
            <label>Update Section</label>
            <input type="text" id="section" placeholder="Enter new section name">
        </div>

        <button class="btn-submit" onclick="updateStudent()">Save Changes</button>

        <p id="message"></p>
    </div>
</div>

<script>
    function showMessage(msg, color) {
        let m = document.getElementById("message");
        m.innerText = msg;
        m.style.color = color === "green" ? "#10b981" : "#ef4444";
        setTimeout(() => { m.innerText = ""; }, 4000);
    }

    function loadStudents() {
        fetch('/students_list')
        .then(r => r.json())
        .then(data => {
            let select = document.getElementById("studentSelect");
            select.innerHTML = '<option value="">Choose a student...</option>';
            data.forEach(s => {
                let option = document.createElement("option");
                option.value = s.id;
                option.text = s.name;
                select.appendChild(option);
            });
        });
    }

    function loadStudent() {
        let id = document.getElementById("studentSelect").value;
        let dataDiv = document.getElementById("studentData");

        if (!id) {
            dataDiv.style.display = "none";
            return;
        }

        fetch('/student/' + id)
        .then(r => r.json())
        .then(data => {
            dataDiv.style.display = "block";
            dataDiv.innerHTML = `
                <div><strong>Current Name:</strong> ${data.name}</div>
                <div><strong>Current Grade:</strong> ${data.grade}</div>
                <div><strong>Current Section:</strong> ${data.section}</div>
            `;
            document.getElementById("grade").value = data.grade;
            document.getElementById("section").value = data.section;
        });
    }

    function updateStudent() {
        let id = document.getElementById("studentSelect").value;
        let grade = document.getElementById("grade").value;
        let section = document.getElementById("section").value;

        if (!id) { showMessage("Please select a student profile", "red"); return; }
        if (!grade || !section) { showMessage("Both fields are required", "red"); return; }

        fetch('/update_student', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({id: id, grade: grade, section: section})
        })
        .then(r => r.json())
        .then(data => {
            showMessage("Database updated successfully!", "green");
            loadStudent();
        });
    }

    loadStudents();
</script>

</body>
</html>
"""

# ==============================
# ROUTES (UNCHANGED LOGIC)
# ==============================

@app.route('/')
def home():
    return render_template_string(html_page)

@app.route('/students_list')
def get_students_list():
    conn = get_db()
    rows = conn.execute("SELECT id, name FROM student").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/student/<int:id>')
def get_single_student(id):
    conn = get_db()
    row = conn.execute("SELECT * FROM student WHERE id=?", (id,)).fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({"message": "Student not found"})

@app.route('/update_student', methods=['POST'])
def update_student():
    data = request.get_json()
    conn = get_db()
    conn.execute("UPDATE student SET grade=?, section=? WHERE id=?", (data["grade"], data["section"], data["id"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Success"})

if __name__ == "__main__":
    app.run(debug=True)
