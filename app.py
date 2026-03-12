from flask import Flask, jsonify, request, render_template_string
import sqlite3

app = Flask(__name__)

# ==============================
# DATABASE SETUP
# ==============================
conn = sqlite3.connect("students.db", check_same_thread=False)
cursor = conn.cursor()

# Create student table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS student (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    grade INTEGER NOT NULL,
    section TEXT NOT NULL
)
""")
conn.commit()

# Insert a default student if table is empty
cursor.execute("SELECT COUNT(*) FROM student")
if cursor.fetchone()[0] == 0:
    cursor.execute(
        "INSERT INTO student (name, grade, section) VALUES (?, ?, ?)",
        ("Jermilyn Azuela", 10, "Zechariah")
    )
    conn.commit()

# ==============================
# HTML UI EMBEDDED
# ==============================
html_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Student API UI</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #eef2f3;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background: white;
            width: 400px;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            text-align: center;
        }
        h2, h3 { color: #333; }
        button {
            padding: 10px 20px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            margin: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover { background: #2980b9; }
        input {
            padding: 8px;
            margin: 10px 0;
            width: 80%;
            border-radius: 5px;
            border: 1px solid #ccc;
        }
        #message {
            margin-top: 10px;
            font-weight: bold;
        }
    </style>
</head>
<body>
<div class="container">
    <h2>Student Information</h2>
    <button onclick="loadStudent()">Load Student</button>
    <p id="studentData"></p>

    <h3>Update Grade</h3>
    <input type="number" id="grade" placeholder="Enter new grade">
    <br>
    <button onclick="updateGrade()">Update Grade</button>

    <h3>Update Section</h3>
    <input type="text" id="section" placeholder="Enter new section">
    <br>
    <button onclick="updateSection()">Update Section</button>

    <p id="message"></p>
</div>

<script>
function loadStudent() {
    fetch('/student')
    .then(response => response.json())
    .then(data => {
        if(data.message){
            document.getElementById("studentData").innerText = data.message;
        } else {
            document.getElementById("studentData").innerHTML =
                "Name: " + data.name + "<br>" +
                "Grade: " + data.grade + "<br>" +
                "Section: " + data.section;
        }
        document.getElementById("message").innerText = "";
    });
}

function updateGrade() {
    let newGrade = document.getElementById("grade").value;
    if(!newGrade){
        document.getElementById("message").innerText = "Please enter a valid grade!";
        document.getElementById("message").style.color = "red";
        return;
    }

    fetch('/update_grade', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({grade: parseInt(newGrade)})
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("message").innerText = data.message;
        document.getElementById("message").style.color = "green";
        loadStudent();
    });
}

function updateSection() {
    let newSection = document.getElementById("section").value;
    if(!newSection){
        document.getElementById("message").innerText = "Please enter a valid section!";
        document.getElementById("message").style.color = "red";
        return;
    }

    fetch('/update_section', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({section: newSection})
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("message").innerText = data.message;
        document.getElementById("message").style.color = "green";
        loadStudent();
    });
}
</script>
</body>
</html>
"""

# ==============================
# FLASK ROUTES
# ==============================

# Homepage (UI)
@app.route('/')
def home():
    return render_template_string(html_page)

# Get student data
@app.route('/student', methods=['GET'])
def get_student():
    cursor.execute("SELECT * FROM student LIMIT 1")
    row = cursor.fetchone()
    if row:
        student_data = {"id": row[0], "name": row[1], "grade": row[2], "section": row[3]}
        return jsonify(student_data)
    return jsonify({"message": "No student found"}), 404

# Update student grade
@app.route('/update_grade', methods=['POST'])
def update_grade():
    data = request.get_json()
    if "grade" not in data:
        return jsonify({"message": "Grade is required"}), 400
    
    new_grade = int(data["grade"])
    cursor.execute("UPDATE student SET grade=? WHERE id=1", (new_grade,))
    conn.commit()
    
    cursor.execute("SELECT * FROM student WHERE id=1")
    row = cursor.fetchone()
    student_data = {"id": row[0], "name": row[1], "grade": row[2], "section": row[3]}
    return jsonify({"message": "Grade updated successfully", "student": student_data})

# Update student section
@app.route('/update_section', methods=['POST'])
def update_section():
    data = request.get_json()
    if "section" not in data:
        return jsonify({"message": "Section is required"}), 400
    
    new_section = data["section"]
    cursor.execute("UPDATE student SET section=? WHERE id=1", (new_section,))
    conn.commit()
    
    cursor.execute("SELECT * FROM student WHERE id=1")
    row = cursor.fetchone()
    student_data = {"id": row[0], "name": row[1], "grade": row[2], "section": row[3]}
    return jsonify({"message": "Section updated successfully", "student": student_data})

# API info
@app.route('/info')
def info():
    return jsonify({
        "API": "Student API",
        "version": "1.0",
        "developer": "Jermilyn Azuela"
    })

# ==============================
# RUN APP
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
