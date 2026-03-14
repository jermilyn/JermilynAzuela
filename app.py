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
    students = [
        ("Jermilyn Azuela", 10, "Zechariah"),
        ("Alice Santos", 9, "Genesis"),
        ("Mark Lopez", 11, "Exodus")
    ]
    for s in students:
        cursor.execute("INSERT OR IGNORE INTO student (name, grade, section) VALUES (?, ?, ?)", s)
    conn.commit()
    conn.close()

init_db()

# ==============================
# HTML USER INTERFACE (MATCHING YOUR SCREENSHOT)
# ==============================
html_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Student Management System</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background: white;
            padding: 40px;
            width: 450px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            text-align: center;
        }
        h2, h3 { color: #333; margin-bottom: 20px; }
        select, input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 6px;
            box-sizing: border-box;
            font-size: 16px;
        }
        button {
            width: 100%;
            padding: 12px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
            margin-bottom: 20px;
        }
        button:hover { background-color: #2980b9; }
        #studentData {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            text-align: left;
            font-size: 15px;
            line-height: 1.6;
            display: none; /* Hidden until a student is selected */
        }
        #message { font-weight: bold; margin-top: 15px; min-height: 20px; }
    </style>
</head>
<body>

<div class="container">
    <h2>Student Information</h2>
    <select id="studentSelect" onchange="loadStudent()">
        <option value="">Select Student</option>
    </select>

    <div id="studentData"></div>

    <h3>Update Grade</h3>
    <input type="number" id="grade" placeholder="New Grade">
    <button onclick="updateGrade()">Update Grade</button>

    <h3>Update Section</h3>
    <input type="text" id="section" placeholder="New Section">
    <button onclick="updateSection()">Update Section</button>

    <p id="message"></p>
</div>

<script>
    // Load list of students into dropdown on page load
    function loadStudents() {
        fetch('/students')
            .then(r => r.json())
            .then(data => {
                let select = document.getElementById("studentSelect");
                select.innerHTML = '<option value="">Select Student</option>';
                data.forEach(s => {
                    let option = document.createElement("option");
                    option.value = s.id;
                    option.text = s.name;
                    select.appendChild(option);
                });
            });
    }

    // Display info for selected student
    function loadStudent() {
        let id = document.getElementById("studentSelect").value;
        let display = document.getElementById("studentData");

        if (!id) {
            display.style.display = "none";
            return;
        }

        fetch('/student/' + id)
            .then(r => r.json())
            .then(data => {
                display.style.display = "block";
                display.innerHTML = `
                    <strong>Name:</strong> ${data.name}<br>
                    <strong>Grade:</strong> ${data.grade}<br>
                    <strong>Section:</strong> ${data.section}
                `;
            });
    }

    function showMessage(msg, color) {
        let m = document.getElementById("message");
        m.innerText = msg;
        m.style.color = color;
        setTimeout(() => { m.innerText = ""; }, 3000);
    }

    function updateGrade() {
        let id = document.getElementById("studentSelect").value;
        let grade = document.getElementById("grade").value;

        if (!id) { showMessage("Please select a student", "red"); return; }
        if (!grade) { showMessage("Please enter a grade", "red"); return; }

        fetch('/update_grade', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({id: id, grade: grade})
        })
        .then(r => r.json())
        .then(data => {
            showMessage(data.message, "green");
            loadStudent();
            document.getElementById("grade").value = "";
        });
    }

    function updateSection() {
        let id = document.getElementById("studentSelect").value;
        let section = document.getElementById("section").value;

        if (!id) { showMessage("Please select a student", "red"); return; }
        if (!section) { showMessage("Please enter a section", "red"); return; }

        fetch('/update_section', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({id: id, section: section})
        })
        .then(r => r.json())
        .then(data => {
            showMessage(data.message, "green");
            loadStudent();
            document.getElementById("section").value = "";
        });
    }

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

@app.route('/students')
def get_students():
    conn = get_db()
    rows = conn.execute("SELECT id, name FROM student").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/student/<int:id>')
def get_student(id):
    conn = get_db()
    row = conn.execute("SELECT * FROM student WHERE id=?", (id,)).fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({"message": "Student not found"}), 404

@app.route('/update_grade', methods=['POST'])
def update_grade():
    data = request.get_json()
    conn = get_db()
    conn.execute("UPDATE student SET grade=? WHERE id=?", (data["grade"], data["id"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Grade updated successfully"})

@app.route('/update_section', methods=['POST'])
def update_section():
    data = request.get_json()
    conn = get_db()
    conn.execute("UPDATE student SET section=? WHERE id=?", (data["section"], data["id"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Section updated successfully"})

if __name__ == "__main__":
    app.run(debug=True)
