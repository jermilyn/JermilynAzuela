from flask import Flask, jsonify, request, render_template_string
from database import init_db, add_student, get_all_students, delete_student

app = Flask(__name__)
init_db()

html_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Student System</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f4f7f6; display: flex; flex-direction: column; align-items: center; padding: 40px; }
        
        /* Navigation Styles */
        .navbar { margin-bottom: 30px; display: flex; gap: 10px; }
        .nav-btn { padding: 10px 20px; border: none; border-radius: 25px; cursor: pointer; font-weight: bold; transition: 0.3s; background: #ddd; }
        .nav-btn.active { background: #5842e3; color: white; }
        
        .card { background: white; width: 450px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: #5842e3; color: white; padding: 25px; text-align: center; }
        .content { padding: 25px; }
        
        label { display: block; font-weight: bold; margin: 10px 0 5px; font-size: 14px; }
        input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; margin-bottom: 10px; }
        
        .btn-register { width: 100%; background: #5842e3; color: white; border: none; padding: 15px; border-radius: 8px; font-weight: bold; cursor: pointer; }
        .list-container { width: 100%; max-width: 850px; background: white; border-radius: 12px; padding: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); display: none; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #eee; }
        .btn-delete { background: #ff4d4d; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>

<div class="navbar">
    <button id="btn-nav-reg" class="nav-btn active" onclick="showSection('reg')">Registration</button>
    <button id="btn-nav-admin" class="nav-btn" onclick="showSection('admin')">Admin Panel</button>
</div>

<div id="section-reg" class="card">
    <div class="header"><h2>Student Registration</h2></div>
    <div class="content">
        <label>Student ID</label><input type="text" id="student_id">
        <label>Full Name</label><input type="text" id="name">
        <label>Age</label><input type="number" id="age">
        <label>Year / Section</label><input type="text" id="year_section">
        <button class="btn-register" onclick="registerStudent()">Register Student</button>
    </div>
</div>

<div id="section-admin" class="list-container">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h3>Registered Students List</h3>
        <button class="nav-btn" onclick="loadStudents()" style="font-size: 12px;">Refresh List</button>
    </div>
    <table>
        <thead>
            <tr>
                <th>ID</th><th>Name</th><th>Age</th><th>Year/Section</th><th>Action</th>
            </tr>
        </thead>
        <tbody id="studentTableBody"></tbody>
    </table>
</div>

<script>
    function showSection(type) {
        const regSec = document.getElementById("section-reg");
        const adminSec = document.getElementById("section-admin");
        const regBtn = document.getElementById("btn-nav-reg");
        const adminBtn = document.getElementById("btn-nav-admin");

        if(type === 'reg') {
            regSec.style.display = "block";
            adminSec.style.display = "none";
            regBtn.classList.add("active");
            adminBtn.classList.remove("active");
        } else {
            regSec.style.display = "none";
            adminSec.style.display = "block";
            adminBtn.classList.add("active");
            regBtn.classList.remove("active");
            loadStudents(); // Load data when opening admin
        }
    }

    function loadStudents() {
        fetch('/students_list').then(r => r.json()).then(data => {
            const tbody = document.getElementById("studentTableBody");
            tbody.innerHTML = "";
            data.forEach(s => {
                tbody.innerHTML += `<tr>
                    <td>${s.student_id}</td>
                    <td>${s.name}</td>
                    <td>${s.age}</td>
                    <td>${s.year_section}</td>
                    <td><button class="btn-delete" onclick="removeStudent('${s.student_id}')">Delete</button></td>
                </tr>`;
            });
        });
    }

    function registerStudent() {
        const data = {
            student_id: document.getElementById("student_id").value,
            name: document.getElementById("name").value,
            age: document.getElementById("age").value,
            year_section: document.getElementById("year_section").value
        };

        if(!data.student_id || !data.name) {
            alert("Please fill in the required fields.");
            return;
        }

        fetch('/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        }).then(r => r.json()).then(res => {
            alert(res.message);
            if(res.status === "success") {
                ["student_id", "name", "age", "year_section"].forEach(id => document.getElementById(id).value = "");
            }
        });
    }

    function removeStudent(id) {
        if(confirm("Are you sure you want to delete this student?")) {
            fetch('/delete/' + id, { method: 'DELETE' })
            .then(r => r.json())
            .then(res => {
                loadStudents();
            });
        }
    }
</script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(html_page)

@app.route('/students_list')
def list_students(): return jsonify(get_all_students())

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    success, msg = add_student(data['student_id'], data['name'], data['age'], data['year_section'])
    return jsonify({"status": "success" if success else "error", "message": msg})

@app.route('/delete/<id>', methods=['DELETE'])
def delete(id):
    success = delete_student(id)
    return jsonify({"status": "success" if success else "error"})

if __name__ == "__main__":
    app.run(debug=True)
