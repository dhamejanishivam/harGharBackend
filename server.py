from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from flask import Response
import uuid # Import uuid for unique IDs
import os
from werkzeug.utils import secure_filename
import uuid # Import uuid for unique IDs

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# https://grx6djfl-5000.inc1.devtunnels.ms/


"""

curl -X POST https://grx6djfl-5000.inc1.devtunnels.ms/login \
-H "Content-Type: application/json" \
-d '{"username": "CGPV001", "password": "hgm@2025"}'


"""





class Database:
    def __init__(self, host="localhost", user="root", password="", database="project"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        self.connect()


    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print("[DB] Connected to MySQL")
        except mysql.connector.Error as err:
            print(f"[DB ERROR] {err}")

    def execute(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor
        except mysql.connector.Error as err:
            print(f"[QUERY ERROR] {err}")
            return None

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("[DB] Connection closed")


app = Flask(__name__)
CORS(app)


# Load the database here
users={
    'CGCO001':'hgm@2025',
    'CGAB001':'hgm@2025',
    'CGPV001':'hgm@2025',
}



@app.route('/')
def homepage():
    return '<body style=background-color:black;color:white;display:flex;align-items:center;justify-content:center;font-size:40px;>WORKING'

@app.route('/data', methods=['GET'])
def show_all_students():
    db = Database(database="project")
    result = db.execute("SELECT * FROM students")
    students = db.fetchall()

    table_headers = students[0].keys() if students else []
    html = """
    <html>
    <head>
        <title>All Student Data</title>
        <style>
            body { background-color: #121212; color: #fff; font-family: sans-serif; padding: 20px; }
            h1 { text-align: center; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #333; padding: 8px; text-align: left; }
            th { background-color: #1f1f1f; }
            tr:nth-child(even) { background-color: #2a2a2a; }
            tr:hover { background-color: #3a3a3a; }
        </style>
    </head>
    <body>
        <h1>All Registered Students</h1>
        <table>
            <tr>""" + "".join(f"<th>{col}</th>" for col in table_headers) + "</tr>"

    for row in students:
        html += "<tr>" + "".join(f"<td>{row[col]}</td>" for col in table_headers) + "</tr>"

    html += """
        </table>
    </body>
    </html>
    """

    return Response(html, mimetype='text/html')






@app.route('/register', methods=['POST'])
def register():
    db = Database(database="project")

    try:
        # Get form fields from request.form - THIS REMAINS CORRECT FOR MULTIPART
        username = request.form.get('username')
        name = request.form.get('name')
        password = request.form.get('username') # STILL GETTING PLAINTEXT PASSWORD - CRITICAL!
        guardian_name = request.form.get('guardian_name')
        father_name = request.form.get('father_name')
        mother_name = request.form.get('mother_name')
        age = request.form.get('age')
        dob = request.form.get('dob') # Assumes YYYY-MM-DD from frontend
        aanganwadi_code = request.form.get('aanganwadi_code')
        weight = request.form.get('weight')
        height = request.form.get('height')
        health_status = request.form.get('health_status')

        # Address parts (from frontend's FormData)
        village = request.form.get('village', '')
        ward = request.form.get('ward', '')
        panchayat = request.form.get('panchayat', '')
        district = request.form.get('district', '')
        block = request.form.get('block', '')
        # The frontend sends 'address' as one combined field, so use that.
        # If you want to store these separately, update your DB schema and INSERT query.
        address = request.form.get('address', '') # Get combined address from frontend

        # Handle files with unique names
        plant_file = request.files.get('plant_photo')
        pledge_file = request.files.get('pledge_photo')

        plant_filename = None
        pledge_filename = None

        totalImagesYet=1

        if plant_file:
            original_filename = secure_filename(plant_file.filename)
            # Generate a unique ID and combine with original extension
            unique_filename = str(uuid.uuid4()) + os.path.splitext(original_filename)[1]
            plant_file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
            plant_filename = unique_filename # Store the unique filename/path in DB

        if pledge_file:
            original_filename = secure_filename(pledge_file.filename)
            unique_filename = str(uuid.uuid4()) + os.path.splitext(original_filename)[1]
            pledge_file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
            pledge_filename = unique_filename # Store the unique filename/path in DB

        query = """
            INSERT INTO students (
                username, name, password, guardian_name, father_name, mother_name,
                age, dob, aanganwadi_code, weight, height, health_status,
                plant_photo, pledge_photo, address,totalImagesYet
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            username, name, password, guardian_name, father_name, mother_name,
            int(age), # Convert to int
            dob,
            int(aanganwadi_code), # Convert to int
            float(weight), # Convert to float
            float(height), # Convert to float
            health_status,
            plant_filename, # This will now be the unique filename
            pledge_filename, # This will now be the unique filename
            address,
            totalImagesYet
        )

        db.execute(query, values)
        return jsonify({'success': True, 'msg': 'Student registered successfully'}), 201

    except Exception as e:
        print("[REGISTER ERROR]", e)
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close() # Ensure connection is closed



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')  # This is contact_number or user_id
    password = data.get('password')

    db = Database(database="project")

    # 1. Try users table
    user_query = "SELECT * FROM users WHERE contact_number = %s AND password_hash = %s"
    result = db.execute(user_query, (username, password))
    user = db.fetchone()

    if user:
        # Normalize role for frontend routing
        role = user.get("role", "").lower()
        if role == "aanganwadi_worker":
            mapped_role = "aanganwadi"
        else:
            mapped_role = "admin"

        return jsonify({
            "success": True,
            "token": None,
            "user": {
                "name":user.get("name"),
                "username": user.get("contact_number"),
                "role": mapped_role
            },
            "role": mapped_role
        }), 200

    # 2. Try students table
    student_query = "SELECT * FROM students WHERE username = %s AND password = %s"
    result = db.execute(student_query, (username, password))
    student = db.fetchone()

    if student:
        return jsonify({
            "success": True,
            "token": None,
            "user": {
                "name": student.get("name"),
                "father_name": student.get("father_name"),
                "mother_name": student.get("mother_name"),
                "guardian_name": student.get("guardian_name"),
                "age": student.get("age"),
                "aanganwadi_code":student.get("aanganwadi_code"),
                "username": student.get("username"),  
                "totalImagesYet": student.get("totalImagesYet"),  
                "role": "family"
            },
            "role": "family"
        }), 200


    return jsonify({
        "success": False,
        "message": "Invalid credentials"
    }), 401


if __name__ == '__main__':
    app.run(debug=True)