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

# Insert default students if table is empty
cursor.execute("SELECT COUNT(*) FROM student")
if cursor.fetchone()[0] == 0:
    cursor.executemany(
        "INSERT INTO student (name, grade, section) VALUES (?, ?, ?)",
        [
            ("Jermilyn Azuela", 10, "Zechariah"),
            ("Alice Santos", 9, "Genesis"),
            ("Mark Lopez", 11, "Exodus")
        ]
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
        body { font-family: Arial; background: #eef2f3; display:flex; justify-content:center; align-items:center; height:100vh; }
        .container { background:white; width:450px; padding:25px; border-radius:12px; box-shadow:0 4px 15px rgba(0,0,0,0.2); text-align:center; }
        h2,h3 { color:#333; }
        select, input { padding:8px; margin:10px 0; width:80%; border-radius:5px; border:1px solid #ccc; }
        button { padding:10px 20px; background:#3498db; color:white; border:none; border-radius:5px; margin:5px; cursor:pointer; transition:0.3s; }
        button:hover { background:#2980b9; }
        #message { margin-top:10px; font-weight:bold; }
    </style>
</head>
<body>
<div class="container">
    <h2>Student Information</h2>
    <select id="studentSelect" onchange="loadStudent()">
        <option value="">-- Select Student --</option>
    </select>
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
// Load all students into dropdown
function loadStudentsDropdown(){
    fetch('/students')
    .then(res => res.json())
    .then(data => {
        const select = document.getElementById("studentSelect");
        select.innerHTML = '<option value="">-- Select Student --</option>';
        data.forEach(student => {
            const option = document.createElement("option");
            option.value = student.id;
            option.text = student.name;
            select.appendChild(option);
        });
    });
}

// Load selected student info
function loadStudent() {
    const studentId = document.getElementById("studentSelect").value;
    if(!studentId) {
        document.getElementById("studentData").innerHTML = "";
        return;
    }
    fetch('/student/' + studentId)
    .then(res => res.json())
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
    const studentId = document.getElementById("studentSelect").value;
    const newGrade = document.getElementById("grade").value;
    if(!studentId) { showMessage("Select a student first", "red"); return; }
    if(!newGrade) { showMessage("Enter a valid grade", "red"); return; }

    fetch('/update_grade', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({id:studentId, grade:parseInt(newGrade)})
    })
    .then(res=>res.json())
    .then(data=>{ showMessage(data.message,"green"); loadStudent(); });
}

function updateSection() {
    const studentId = document.getElementById("studentSelect").value;
    const newSection = document.getElementById("section").value;
    if(!studentId) { showMessage("Select a student first","red"); return; }
    if(!newSection) { showMessage("Enter a valid section","red"); return; }

    fetch('/update_section', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({id:studentId, section:newSection})
    })
    .then(res=>res.json())
    .then(data=>{ showMessage(data.message,"green"); loadStudent(); });
}

function showMessage(msg,color){ 
    const message = document.getElementById("message"); 
    message.innerText = msg; 
    message.style.color = color; 
}

// Initialize dropdown on page load
loadStudentsDropdown();
</script>
</body>
</html>
"""

# ==============================
# FLASK ROUTES
# ==============================

@app.route('/')
def home():
    return render_template_string(html_page)

# Get all students (for dropdown)
@app.route('/students', methods=['GET'])
def get_students():
    cursor.execute("SELECT id, name FROM student")
    rows = cursor.fetchall()
    data = [{"id":r[0], "name":r[1]} for r in rows]
    return jsonify(data)

# Get a specific student
@app.route('/student/<int:id>', methods=['GET'])
def get_student(id):
    cursor.execute("SELECT * FROM student WHERE id=?", (id,))
    row = cursor.fetchone()
    if row:
        return jsonify({"id": row[0], "name": row[1], "grade": row[2], "section": row[3]})
    return jsonify({"message": "Student not found"}), 404

# Update grade
@app.route('/update_grade', methods=['POST'])
def update_grade():
    data = request.get_json()
    if not data.get("id") or "grade" not in data:
        return jsonify({"message":"Student ID and grade required"}),400
    cursor.execute("UPDATE student SET grade=? WHERE id=?",(data["grade"], data["id"]))
    conn.commit()
    return jsonify({"message":"Grade updated successfully"})

# Update section
@app.route('/update_section', methods=['POST'])
def update_section():
    data = request.get_json()
    if not data.get("id") or "section" not in data:
        return jsonify({"message":"Student ID and section required"}),400
    cursor.execute("UPDATE student SET section=? WHERE id=?",(data["section"], data["id"]))
    conn.commit()
    return jsonify({"message":"Section updated successfully"})

# API info
@app.route('/info')
def info():
    return jsonify({"API":"Student API","version":"1.1","developer":"Jermilyn Azuela"})

# ==============================
# RUN APP
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
