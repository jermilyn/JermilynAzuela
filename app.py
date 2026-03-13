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

# Insert default students only if they don't exist
students = [
    ("Jermilyn Azuela", 10, "Zechariah"),
    ("Alice Santos", 9, "Genesis"),
    ("Mark Lopez", 11, "Exodus")
]

for s in students:
    cursor.execute(
        "INSERT OR IGNORE INTO student (name, grade, section) VALUES (?, ?, ?)", s
    )

conn.commit()
conn.close()


# ==============================
# HTML USER INTERFACE
# ==============================
html_page = """
<!DOCTYPE html>
<html>
<head>
<title>Student API</title>
<style>
body{
font-family:Arial;
background:#eef2f3;
display:flex;
justify-content:center;
align-items:center;
height:100vh;
}

.container{
background:white;
padding:25px;
width:420px;
border-radius:10px;
box-shadow:0 4px 10px rgba(0,0,0,0.2);
text-align:center;
}

button{
padding:10px;
background:#3498db;
color:white;
border:none;
border-radius:5px;
margin:5px;
cursor:pointer;
}

button:hover{
background:#2980b9;
}

select,input{
padding:8px;
margin:8px;
width:80%;
}

#message{
font-weight:bold;
margin-top:10px;
}
</style>
</head>

<body>

<div class="container">

<h2>Student Information</h2>

<select id="studentSelect" onchange="loadStudent()">
<option value="">Select Student</option>
</select>

<p id="studentData"></p>

<h3>Update Grade</h3>
<input type="number" id="grade" placeholder="New Grade">
<br>
<button onclick="updateGrade()">Update Grade</button>

<h3>Update Section</h3>
<input type="text" id="section" placeholder="New Section">
<br>
<button onclick="updateSection()">Update Section</button>

<p id="message"></p>

</div>

<script>

function showMessage(msg,color){
let m=document.getElementById("message");
m.innerText=msg;
m.style.color=color;
}

function loadStudents(){
fetch('/students')
.then(r=>r.json())
.then(data=>{
let select=document.getElementById("studentSelect");
select.innerHTML='<option value="">Select Student</option>';

data.forEach(s=>{
let option=document.createElement("option");
option.value=s.id;
option.text=s.name;
select.appendChild(option);
});
});
}

function loadStudent(){
let id=document.getElementById("studentSelect").value;

if(!id){
document.getElementById("studentData").innerHTML="";
return;
}

fetch('/student/'+id)
.then(r=>r.json())
.then(data=>{
document.getElementById("studentData").innerHTML=
"Name: "+data.name+"<br>"+
"Grade: "+data.grade+"<br>"+
"Section: "+data.section;
});
}

function updateGrade(){
let id=document.getElementById("studentSelect").value;
let grade=document.getElementById("grade").value;

if(!id){showMessage("Select student first","red");return;}
if(!grade){showMessage("Enter grade","red");return;}

fetch('/update_grade',{
method:'POST',
headers:{'Content-Type':'application/json'},
body:JSON.stringify({id:id,grade:grade})
})
.then(r=>r.json())
.then(data=>{
showMessage(data.message,"green");
loadStudent();
});
}

function updateSection(){
let id=document.getElementById("studentSelect").value;
let section=document.getElementById("section").value;

if(!id){showMessage("Select student first","red");return;}
if(!section){showMessage("Enter section","red");return;}

fetch('/update_section',{
method:'POST',
headers:{'Content-Type':'application/json'},
body:JSON.stringify({id:id,section:section})
})
.then(r=>r.json())
.then(data=>{
showMessage(data.message,"green");
loadStudent();
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
def students():
    conn = get_db()
    cursor = conn.cursor()

    rows = cursor.execute("SELECT id,name FROM student").fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route('/student/<int:id>')
def student(id):
    conn = get_db()
    cursor = conn.cursor()

    row = cursor.execute(
        "SELECT * FROM student WHERE id=?", (id,)
    ).fetchone()

    conn.close()

    if row:
        return jsonify(dict(row))

    return jsonify({"message": "Student not found"})


@app.route('/update_grade', methods=['POST'])
def update_grade():
    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE student SET grade=? WHERE id=?",
        (data["grade"], data["id"])
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Grade updated successfully"})


@app.route('/update_section', methods=['POST'])
def update_section():
    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE student SET section=? WHERE id=?",
        (data["section"], data["id"])
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Section updated successfully"})


@app.route('/info')
def info():
    return jsonify({
        "API": "Student API",
        "version": "2.0",
        "developer": "Jermilyn Azuela"
    })


# ==============================
# RUN SERVER
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
