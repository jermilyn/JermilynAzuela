from flask import Flask, jsonify, request

app = Flask(__name__)

# Sample data (temporary database)
students = [
    {
        "id": 1,
        "name": "Jermilyn Azuela",
        "grade": 10,
        "section": "Zechariah"
    }
]

# Home route
@app.route('/')
def home():
    return "Welcome to my Flask API!"

# Get all students
@app.route('/students', methods=['GET'])
def get_students():
    return jsonify(students)

# Get a single student by ID
@app.route('/student/<int:id>', methods=['GET'])
def get_student(id):
    for student in students:
        if student["id"] == id:
            return jsonify(student)
    return jsonify({"error": "Student not found"}), 404

# Add a new student
@app.route('/student', methods=['POST'])
def add_student():
    data = request.get_json()

    new_student = {
        "id": len(students) + 1,
        "name": data.get("name"),
        "grade": data.get("grade"),
        "section": data.get("section")
    }

    students.append(new_student)

    return jsonify({
        "message": "Student added successfully",
        "student": new_student
    })

# Update student grade
@app.route('/student/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()

    for student in students:
        if student["id"] == id:
            student["grade"] = data.get("grade", student["grade"])
            student["section"] = data.get("section", student["section"])
            return jsonify({
                "message": "Student updated successfully",
                "student": student
            })

    return jsonify({"error": "Student not found"}), 404

# Delete a student
@app.route('/student/<int:id>', methods=['DELETE'])
def delete_student(id):
    for student in students:
        if student["id"] == id:
            students.remove(student)
            return jsonify({"message": "Student deleted successfully"})

    return jsonify({"error": "Student not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
