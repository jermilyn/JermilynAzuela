from flask import Flask, jsonify, request, render_template_string
import sqlite3

app = Flask(__name__)

# ==============================
# DATABASE CONNECTION FUNCTION
# ==============================
def get_db():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn

# ==============================
# DATABASE SETUP
# ==============================
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
    # Changed variable name to default_students to avoid naming conflicts
    default_students = [
        ("Jermilyn Azuela", 10, "Zechariah"),
        ("Alice Santos", 9, "Genesis"),
        ("Mark Lopez", 11, "Exodus")
    ]
    for s in default_students:
        cursor.execute(
            "INSERT OR IGNORE INTO student (name, grade, section) VALUES (?, ?, ?)", s
        )
    conn.commit()
    conn.close()

init_db()

# ==============================
# HTML USER INTERFACE
# ==============================
html_page = """
<!DOCTYPE html>
<html>
<head>
<title>Student Management</title>
<style>
body {
    font-family: 'Segoe UI', Arial, sans-serif;
    background: #f0f2f5;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    margin: 0;
}

.container {
    background: white;
    padding: 30px;
    width: 400px;
    border-radius: 15px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.1);
    text-align: center;
}

h2 { margin-bottom: 25px; font-weight: bold; }
h3 { margin-top: 20px; font-size: 1.2em; }

button {
    padding: 10px 20px;
    background: #3498db;
    color: white;
    border: none;
    border-radius: 5px;
    width: 85%;
    cursor: pointer;
    font-weight: bold;
    transition: 0.3s;
}

button:hover { background: #2980b9; }

select, input {
    padding: 10px;
    margin: 10px 0;
    width: 80%;
    border: 1px solid #ccc;
    border-radius: 4px;
}

#studentData {
    margin: 15px 0;
    padding: 10px;
    background: #f9f9f9;
    border-radius: 5px;
    font-size: 0.9em;
    color: #555;
    text-align: left;
    display: inline-block;
    width: 80%;
}

#message {
    font-weight: bold;
    margin-top: 15px;
    font-size: 0.9em;
}
</style>
</head>
<body>

<div class="container">
    <h2>Student Information</h2>

    <select id="studentSelect" onchange="loadStudent()">
        <option value="">Select Student</option>
    </select>

    <div id="studentData" style="display:none;"></div>

    <h3>Update Grade</h3>
    <input type="number" id="grade" placeholder="New Grade">
    <button onclick="updateGrade()">Update Grade</button>

    <h3>Update Section</h3>
    <input type="text" id="section" placeholder="New Section">
    <button onclick="updateSection()">Update Section</button>

    <p id="message"></p>
</div>

<script>
function showMessage(msg, color){
    let m = document.getElementById("message");
    m.innerText = msg;
    m.style.color = color;
    setTimeout(() => { m.innerText = ""; }, 3000);
}

function loadStudents(){
    fetch('/students_list')
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

function loadStudent(){
    let id = document.getElementById("studentSelect").value;
    let dataDiv = document.getElementById("studentData");

    if(!id){
        dataDiv.style.display = "none";
        return;
    }

    fetch('/student/' + id)
    .then(r => r.json())
    .then(data => {
        dataDiv.style.display = "block";
        dataDiv.innerHTML = 
            "<strong>Name:</strong> " + data.name + "<br>" +
            "<strong>Grade:</strong> " + data.grade + "<br>" +
            "<strong>Section:</strong> " + data.section;
    });
}

function updateGrade(){
    let id = document.getElementById("studentSelect").value;
    let grade = document.getElementById("grade").value;

    if(!id){ showMessage("Select student first", "red"); return; }
    if(!grade){ showMessage("Enter grade", "red"); return; }

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

function updateSection(){
    let id = document.getElementById("studentSelect").value;
    let section = document.getElementById("section").value;

    if(!id){ showMessage("Select student first", "red"); return; }
    if(!section){ showMessage("Enter section", "red"); return; }

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

@app.route('/students_list') # Changed from /students to avoid variable conflict
def get_students_list():
    conn = get_db()
    cursor = conn.cursor()
    rows = cursor.execute("SELECT id, name FROM student").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/student/<int:id>')
def get_single_student(id):
    conn = get_db()
    cursor = conn.cursor()
    row = cursor.execute("SELECT * FROM student WHERE id=?", (id,)).fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({"message": "Student not found"})

@app.route('/update_grade', methods=['POST'])
def update_grade():
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE student SET grade=? WHERE id=?", (data["grade"], data["id"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Grade updated successfully"})

@app.route('/update_section', methods=['POST'])
def update_section():
    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE student SET section=? WHERE id=?", (data["section"], data["id"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Section updated successfully"})

if __name__ == "__main__":
    app.run(debug=True)
