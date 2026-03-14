<?php
// ==============================
// DATABASE CONNECTION FUNCTION
// ==============================
function get_db() {
    try {
        // Connect to the SQLite database file
        $pdo = new PDO("sqlite:students.db");
        
        // Set error mode to exceptions so we can catch issues
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        
        // Return results as associative arrays (similar to sqlite3.Row)
        $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
        
        return $pdo;
    } catch (PDOException $e) {
        die("Could not connect to the database: " . $e->getMessage());
    }
}

// ==============================
// DATABASE SETUP
// ==============================
$db = get_db();

// Create Table
$db->exec("CREATE TABLE IF NOT EXISTS student (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    grade INTEGER,
    section TEXT
)");

// Default Students Data
$students = [
    ['Jermilyn Azuela', 10, 'Zechariah'],
    ['Alice Santos', 9, 'Genesis'],
    ['Mark Lopez', 11, 'Exodus']
];

// Insert default students only if they don't exist
$stmt = $db->prepare("INSERT OR IGNORE INTO student (name, grade, section) VALUES (?, ?, ?)");

foreach ($students as $s) {
    $stmt->execute($s);
}

// Note: In PHP/PDO, the connection closes automatically when the script ends.
?>
