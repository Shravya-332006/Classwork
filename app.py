from flask import Flask, request, render_template
import sqlite3
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
# Define the database file name
DATABASE = 'students.sqlite'

# --- Database Functions ---

def init_db():
    """Initializes the database by creating the 'attendance' table."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Create a table to store attendance records
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            submission_time DATETIME NOT NULL,
            ip_address TEXT
        );
    ''')
    conn.commit()
    conn.close()

def record_attendance(name, ip):
    """Inserts a new attendance record into the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    current_time = datetime.now()
    
    # Use parameter substitution (?) to prevent SQL Injection
    cursor.execute(
        "INSERT INTO attendance (student_name, submission_time, ip_address) VALUES (?, ?, ?)", 
        (name, current_time, ip)
    )
    
    conn.commit()
    conn.close()

def get_attendance_records():
    """Retrieves all attendance records."""
    conn = sqlite3.connect(DATABASE)
    # Set row_factory to sqlite3.Row to access columns by name
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance ORDER BY submission_time DESC")
    records = cursor.fetchall()
    conn.close()
    return records

# --- Flask Routes ---

@app.route('/', methods=['GET', 'POST'])
def home():
    """Handles the attendance submission form and displays the result."""
    attendance_message = None
    
    if request.method == 'POST':
        student_name = request.form.get('student_name')
        
        if student_name:
            # Get the user's IP address (useful for tracking/preventing double submissions)
            user_ip = request.remote_addr 
            
            record_attendance(student_name, user_ip)
            attendance_message = f"Attendance recorded for **{student_name}** at {datetime.now().strftime('%H:%M:%S')}!"
        else:
            attendance_message = "Please enter your name."
    
    return render_template('index.html', message=attendance_message)

@app.route('/view_records')
def view_records():
    """Displays all recorded attendance records."""
    records = get_attendance_records()
    return render_template('records.html', records=records)

# --- Run the Application ---

if __name__ == '__main__':
    # Initialize the database table when the app starts
    init_db() 
    # Run the application in debug mode
    app.run(debug=True)
