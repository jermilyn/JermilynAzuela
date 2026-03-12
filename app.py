from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# Sample student data
student = {
    "name": "Jermilyn Azuela",
    "grade": 10,
    "section": "Zechariah"
}

# HTML UI embedded
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
            color: green;
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

    <p id="message"></p>
</div>

<script>
function loadStudent() {
    fetch('/student')
    .then(response => response.json())
    .then(data => {
        document.getElementById("studentData").innerHTML =
            "Name: " + data.name + "<br>" +
            "Grade: " + data.grade + "<br>" +
            "Section: " + data.section;
        document.getElementById("message").innerText = "";
    });
}

function updateGrade() {
    let newGrade = document.getElementById("grade").value;
    if(!newGrade) {
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
</script>
</body>
</html>
"""

# Homepage (UI)
@app.route('/')
def home():
    return render_template_string(html_page)

# Get student data
@app.route('/student', methods=['GET'])
def get_student():
    return jsonify(student)

# Update student grade
@app.route('/update_grade', methods=['POST'])
def update_grade():
    data = request.get_json()
    if "grade" in data:
        student["grade"] = data["grade"]
    return jsonify({
        "message": "Grade updated successfully",
        "student": student
    })

# API information
@app.route('/info')
def info():
    return jsonify({
        "API": "Student API",
        "version": "1.0",
        "developer": "Jermilyn Azuela"
    })

if __name__ == "__main__":
    app.run(debug=True)
