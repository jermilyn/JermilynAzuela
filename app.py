from flask import Flask, jsonify, request, render_template_string
import sqlite3

app = Flask(__name__)

# ==============================
# DATABASE CONNECTION
# ==============================
def get_db():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn

# Database Setup (Run once)
def init_db():
    conn = get_db()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS student (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        grade INTEGER,
        section TEXT
    )
    """)
    # Default data
    students = [("Jermilyn Azuela", 24, "Zecha"), ("Alice Santos", 9, "Genesis")]
    for s in students:
        conn.execute("INSERT OR IGNORE INTO student (name, grade, section) VALUES (?, ?, ?)", s)
    conn.commit()
    conn.close()

init_db()

# ==============================
# FIXED UI DESIGN
# ==============================
html_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Manager</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f4f7f6; display: flex; justify-content: center; padding: 40px; }
        .card { background: white; width: 450px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: #5842e3; color: white; padding: 25px; text-align: center; }
        .header h2 { margin: 0; font-size: 24px; }
        .header p { margin: 5px 0 0; opacity: 0.8; font-size: 14px; }
        .content { padding: 25px; }
        
        label { display: block; font-weight: bold; margin: 15px 0 5px; color: #333; }
        select, input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; font-size: 16px; }
        
        .info-box { background: #f0f4ff; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px dashed #5842e3; display: none; }
        .info-box p { margin: 4px 0; font-size: 14px; }
        .info-box strong { color: #5842e3; }

        .btn-save { 
            width: 100%; background: #5842e3; color: white; border: none; padding: 15px; 
            border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 20px;
            transition: 0.2s;
        }
        .btn-save:hover { background: #4532b5; }
        .btn-save:disabled { background: #a59ae0; cursor: not-allowed; }
        
        #message { text-align: center; font-weight: bold; margin-top: 15px; }
    </style>
</head>
<body>

<div class="card">
    <div class="header">
        <h2>Student Information</h2>
        <p>Database Management System</p>
    </div>

    <div class="content">
        <label>Select Student Profile</label>
        <select id="studentSelect" onchange="loadStudent()">
            <option value="">Choose Student...</option>
        </select>

        <div id="studentData" class="info-box"></div>

        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">

        <label>Update Grade</label>
        <input type="number" id="grade" placeholder="Enter grade">

        <label>Update Section</label>
        <input type="text" id="section" placeholder="Enter section">

        <button type="button" id="saveBtn" class="btn-save" onclick="updateStudent()">Save Changes</button>
        <p id="message"></p>
    </div>
</div>

<script>
    function showMessage(msg, color) {
        const m = document.getElementById("message");
        m.innerText = msg;
        m.style.color = color === "green" ? "#2ecc71" : "#e74c3c";
    }

    // Load initial dropdown list
    function loadStudents() {
        fetch('/students_list').then(r => r.json()).then(data => {
            let select = document.getElementById("studentSelect");
            select.innerHTML = '<option value="">Choose Student...</option>';
            data.forEach(s => {
                let opt = document.createElement("option");
                opt.value = s.id; opt.text = s.name;
                select.appendChild(opt);
            });
        });
    }

    // Load selected student details
    function loadStudent() {
        let id = document.getElementById("studentSelect").value;
        let box = document.getElementById("studentData");
        if(!id) { box.style.display = "none"; return; }

        fetch('/student/' + id).then(r => r.json()).then(data => {
            box.style.display = "block";
            box.innerHTML = `
                <p><strong>Current Name:</strong> ${data.name}</p>
                <p><strong>Current Grade:</strong> ${data.grade}</p>
                <p><strong>Current Section:</strong> ${data.section}</p>
            `;
            document.getElementById("grade").value = data.grade;
            document.getElementById("section").value = data.section;
        });
    }

    // The logic to update everything on ONE click
    function updateStudent() {
        const id = document.getElementById("studentSelect").value;
        const grade = document.getElementById("grade").value;
        const section = document.getElementById("section").value;
        const btn = document.getElementById("saveBtn");

        if(!id) { showMessage("Please select a student", "red"); return; }

        // 1. Show immediate visual feedback
        btn.innerText = "Saving...";
        btn.disabled = true;

        fetch('/update_student', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({id: id, grade: grade, section: section})
        })
        .then(response => {
            if (!response.ok) throw new Error('Server error');
            return response.json();
        })
        .then(data => {
            // 2. Success feedback
            showMessage("Updated successfully!", "green");
            loadStudent(); // Refresh the current info box
        })
        .catch(error => {
            showMessage("Error: Could not save", "red");
            console.error(error);
        })
        .finally(() => {
            // 3. Reset button
            btn.innerText = "Save Changes";
            btn.disabled = false;
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

@app.route('/students_list')
def list_students():
    conn = get_db()
    rows = conn.execute("SELECT id, name FROM student").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/student/<int:id>')
def get_student(id):
    conn = get_db()
    row = conn.execute("SELECT * FROM student WHERE id=?", (id,)).fetchone()
    return jsonify(dict(row)) if row else jsonify({})

@app.route('/update_student', methods=['POST'])
def update():
    data = request.get_json()
    conn = get_db()
    conn.execute("UPDATE student SET grade=?, section=? WHERE id=?", 
                 (data['grade'], data['section'], data['id']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True)
