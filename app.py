from flask import Flask, jsonify, request

app = Flask(__name__)

# Sample student data
student = {
    "name": "Jermilyn Azuela",
    "grade": 10,
    "section": "Zechariah"
}

# Home route
@app.route('/')
def home():
    return "Welcome to my Flask API!"

# Get student information
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

# Add subject endpoint
@app.route('/subjects', methods=['GET'])
def get_subjects():
    subjects = ["Math", "Science", "English", "Computer"]
    return jsonify({
        "subjects": subjects
    })

# API information
@app.route('/info', methods=['GET'])
def info():
    return jsonify({
        "API": "Student Information API",
        "version": "1.0",
        "developer": "Jermilyn Azuela"
    })

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
