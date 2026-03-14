from flask import Flask, jsonify, request, render_template_string
import sqlite3

app = Flask(__name__)

# ==============================
# DATABASE CONNECTION
# ==============================
def get_db_connection():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn

# ==============================
# UI DESIGN (Info Box at Bottom)
# ==============================
html_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Manager</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; display: flex; justify-content: center; padding: 40px; margin: 0; }
        .card { background: white; width: 450px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: #5842e3; color: white; padding: 25px; text-align: center; }
        .header h2 { margin: 0; font-size: 24px; }
        
        .content { padding: 25px; }
        label { display: block; font-weight: 600; margin: 15px 0 5px; color: #1e293b; font-size: 14px; }
        
        select, input { 
            width: 100%; padding: 12px; border: 1px solid #e2e8f0; 
            border-radius: 8px; box-sizing: border-box; font-size: 16px; background: #fff; margin-bottom: 10px;
        }

        .btn-save { 
            width: 100%; background: #5842e3; color: white; border: none; padding: 16px; 
            border-radius: 10px; font-size: 16px; font-weight: bold; cursor: pointer; 
            margin-top: 10px; transition: 0.3s;
        }
        .btn-save:hover { background: #4532b5; }

        /* THE BOTTOM INFO BOX */
        .info-box { 
            background: #f0f4ff; padding: 15px; border-radius: 10px; 
            margin-top: 25px; border: 1px solid #d1d9e6; display: none; 
        }
        .info-box p { margin: 5px 0; font-size: 15px; color: #334155; }
        .info-box strong { color: #5842e3; }
        
        #message { text-align: center; font-weight: 600; margin-top: 15px; font-size: 14px; }
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

        <label>Update Grade</label>
        <input type="number" id="grade" placeholder="New Grade">

        <label>Update Section</label>
        <input type="text" id="section" placeholder="New Section">

        <button type="button" id="saveBtn" class="btn-save" onclick="updateStudent()">Save Changes</button>
        
        <p id="message"></p>

        <div id="studentData" class="info-box"></div>
    </div>
</div>

<script>
    function showMessage(msg, color) {
        const m = document.getElementById("message");
        m.innerText = msg;
        m.style.color = color === "green" ? "#10b981" : "#ef4444";
        setTimeout(() => { m.innerText = ""; }, 3000);
    }

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

    function updateStudent() {
        const id = document.getElementById("studentSelect").value;
        const grade = document.getElementById("grade").value;
        const section = document.getElementById("section").value;
        const btn = document.getElementById("saveBtn");

        if(!id) { showMessage("Please select a student", "red"); return; }

        btn.innerText = "Saving...";
        btn.disabled = true;

        fetch('/update_student', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({id: id, grade: grade, section: section})
        })
        .then(r => r.json())
        .then(data => {
            showMessage("Changes saved successfully!", "green");
            loadStudent(); // Refresh the info box at the bottom
        })
        .finally(() => {
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
    with get_db_connection() as conn:
        rows = conn.execute("SELECT id, name FROM student").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/student/<int:id>')
def get_student(id):
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM student WHERE id=?", (id,)).fetchone()
    return jsonify(dict(row)) if row else jsonify({})

@app.route('/update_student', methods=['POST'])
def update():
    data = request.get_json()
    with get_db_connection() as conn:
        conn.execute("UPDATE student SET grade=?, section=? WHERE id=?", 
                     (data['grade'], data['section'], data['id']))
        conn.commit()
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True)
