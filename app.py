from flask import Flask, jsonify, request

# Create Flask app
app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return "Welcome to my Flask API!"

# Get student information
@app.route('/student', methods=['GET'])
def get_student():
    student = {
        "name": "Jermilyn Azuela",
        "grade": 10,
        "section": "Zechariah"
    }
    return jsonify(student)

# Add a new student (example of POST request)
@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.get_json()

    student = {
        "name": data.get("name"),
        "grade": data.get("grade"),
        "section": data.get("section")
    }

    return jsonify({
        "message": "Student added successfully",
        "student": student
    })

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
