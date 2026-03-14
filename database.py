import sqlite3

DB_NAME = "student_registration.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    query = """
    CREATE TABLE IF NOT EXISTS student (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        year_section TEXT NOT NULL
    )
    """
    with get_db_connection() as conn:
        conn.execute(query)
        conn.commit()

def add_student(student_id, name, age, year_section):
    query = "INSERT INTO student (student_id, name, age, year_section) VALUES (?, ?, ?, ?)"
    try:
        with get_db_connection() as conn:
            conn.execute(query, (student_id, name, age, year_section))
            conn.commit()
        return True, "Registration successful"
    except sqlite3.IntegrityError:
        return False, "Error: Student ID already exists"

def get_all_students():
    query = "SELECT * FROM student ORDER BY id DESC"
    with get_db_connection() as conn:
        rows = conn.execute(query).fetchall()
    return [dict(row) for row in rows]

def update_student(student_id, name, age, year_section):
    """Updates an existing student's details based on their unique Student ID."""
    query = """
    UPDATE student 
    SET name = ?, age = ?, year_section = ? 
    WHERE student_id = ?
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(query, (name, age, year_section, student_id))
            conn.commit()
            # Check if any row was actually updated
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Update Error: {e}")
        return False

def delete_student(student_id):
    """Deletes a student based on their unique Student ID."""
    query = "DELETE FROM student WHERE student_id = ?"
    try:
        with get_db_connection() as conn:
            conn.execute(query, (student_id,))
            conn.commit()
        return True
    except Exception:
        return False
