# HARGHAR

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from flask import Response
import uuid
import os
from werkzeug.utils import secure_filename
import datetime
import model
from datetime import datetime

database_name='project'

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# a = int(input("Enter 1 for production and 0 for local development: "))
# production_global = True if a == 1 else False
production_global = True 

app = Flask(__name__, static_folder=UPLOAD_FOLDER, static_url_path='/static')
CORS(app)

app.config['SERVER_NAME'] = 'grx6djfl-5001.inc1.devtunnels.ms'
app.config['PREFERRED_URL_SCHEME'] = 'https'

class ImagePredict:
    def __init__(self):
        self.aiObject = model.IMAGECLASSIFIER()
    def imagePredictor(self,image_path):
        lis = ["NOT MUNGA", "MUNGA"]
        result = self.aiObject.predict(image_path)
        classPredicted=result[0]
        confidence=result[1]
        return lis[classPredicted],confidence

class Database:
    def __init__(self, host="localhost", user="root", password="", database="project", production=False):
        global production_global
        production = production_global 
        if production:
            database_name_prod = "hgm"
            self.host = '127.0.0.1'
            self.user = 'root'
            self.password = 'Ssipmt@2025DODB'
            self.database = database_name_prod
        else:
            self.host = 'localhost'
            self.user = 'root'
            self.password = ''
            self.database = database_name

        self.connection = None
        self.cursor = None
        self._connected = False
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


users={
    'CGCO001':'hgm@2025',
    'CGAB001':'hgm@2025',
    'CGPV001':'hgm@2025',
}

@app.route('/')
def homepage():
    return '<body style=background-color:black;color:white;display:flex;align-items:center;justify-content:center;font-size:40px;>WORKING'

@app.route('/test-image/<filename>')
def test_image(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        return jsonify({'error': 'File not found or access issue', 'details': str(e)}), 404

@app.route('/search2')
def search2Results():
    db = Database(database=database_name)
    try:
        query_total_students = "SELECT COUNT(*) AS total_students FROM students"
        db.execute(query_total_students)
        total_students_result = db.fetchone()
        total_students = total_students_result['total_students'] if total_students_result else 0

        query_total_images = "SELECT SUM(totalImagesYet) AS total_images_uploaded FROM students"
        db.execute(query_total_images)
        total_images_result = db.fetchone()
        total_images_uploaded = total_images_result['total_images_uploaded'] if total_images_result and total_images_result['total_images_uploaded'] is not None else 0

        query_latest_student_name = "SELECT name FROM students ORDER BY id DESC LIMIT 1"
        db.execute(query_latest_student_name)
        latest_student_result = db.fetchone()
        latest_student_name = latest_student_result['name'] if latest_student_result else None

        return jsonify({
            "success": True,
            "total_students": total_students,
            "total_images_uploaded": total_images_uploaded,
            "latest_student_name": latest_student_name
        }), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
    finally:
        db.close()

@app.route('/families/user/<string:user_id>', methods=['GET'])
def get_family_by_user_id(user_id):
    db = Database(database=database_name)
    try:
        query = """
            SELECT
                id,
                username,
                name AS childName,
                guardian_name AS parentName,
                mother_name AS motherName,
                father_name AS fatherName,
                mobile AS mobileNumber,
                address AS village,
                age,
                dob AS dateOfBirth,
                weight,
                height,
                aanganwadi_code AS anganwadiCode,
                plant_photo,
                pledge_photo,
                totalImagesYet,
                health_status
            FROM
                students
            WHERE
                username = %s
        """
        db.execute(query, (user_id,))
        family_data = db.fetchone()

        if family_data:
            base_url = f"{app.config.get('PREFERRED_URL_SCHEME', 'http')}://{app.config['SERVER_NAME']}"

            if family_data.get('plant_photo'):
                family_data['plant_photo'] = f"{base_url}{app.static_url_path}/{family_data['plant_photo']}"
            if family_data.get('pledge_photo'):
                family_data['pledge_photo'] = f"{base_url}{app.static_url_path}/{family_data['pledge_photo']}"

            family_data['totalImagesYet'] = int(family_data.get('totalImagesYet', 0))

            return jsonify(family_data), 200
        else:
            return jsonify({'message': 'Family data not found for this user.'}), 404

    except mysql.connector.Error as db_err:
        return jsonify({'error': 'Database error', 'message': str(db_err)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
    finally:
        db.close()

@app.route('/families/user1/<string:user_id>', methods=['GET'])
def get_family_by_user_id1(user_id):
    db = Database(database=database_name)
    try:
        query = """
            SELECT
                id,
                username,
                name AS childName,
                guardian_name AS parentName,
                mother_name AS motherName,
                father_name AS fatherName,
                mobile AS mobileNumber,
                address AS village,
                age,
                dob AS dateOfBirth,
                weight,
                height,
                aanganwadi_code AS anganwadiCode,
                plant_photo,
                pledge_photo,
                totalImagesYet,
                health_status
            FROM
                students
            WHERE
                id = %s
        """
        db.execute(query, (str(user_id),))
        family_data = db.fetchone()

        if family_data:
            base_url = f"{app.config.get('PREFERRED_URL_SCHEME', 'http')}://{app.config['SERVER_NAME']}"

            if family_data.get('plant_photo'):
                family_data['plant_photo'] = f"{base_url}{app.static_url_path}/{family_data['plant_photo']}"
            if family_data.get('pledge_photo'):
                family_data['pledge_photo'] = f"{base_url}{app.static_url_path}/{family_data['pledge_photo']}"

            family_data['totalImagesYet'] = int(family_data.get('totalImagesYet', 0))

            return jsonify(family_data), 200
        else:
            return jsonify({'message': 'Family data not found for this user.'}), 404

    except mysql.connector.Error as db_err:
        return jsonify({'error': 'Database error', 'message': str(db_err)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
    finally:
        db.close()

@app.route('/searchAng', methods=['GET'])
def searchAng():
    db = Database(database=database_name)
    try:
        query = "SELECT id, name, contact_number, role, created_at, aanganwaadi_id, gram, block, tehsil, zila FROM users"
        db.execute(query)
        users_data = db.fetchall()

        if users_data:
            return jsonify(users_data), 200
        else:
            return jsonify([]), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
    finally:
        db.close()

@app.route('/registerAng', methods=['POST'])
def registerAng():
    db = Database(database=database_name)
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "message": "No JSON data provided"}), 400

        name = data.get('name')
        contact_number = data.get('contact_number')
        password_hash = data.get('password_hash')
        role = data.get('role')
        aanganwaadi_id = data.get('aanganwaadi_id')
        gram = data.get('gram')
        block = data.get('block')
        tehsil = data.get('tehsil')
        zila = data.get('zila')

        if not all([name, contact_number, password_hash, role]):
            return jsonify({"success": False, "message": "Missing required fields (name, contact_number, password_hash, role)"}), 400

        allowed_roles = ['admin', 'aanganwadi_worker', 'health_worker']
        if role not in allowed_roles:
            return jsonify({"success": False, "message": f"Invalid role: {role}. Allowed roles are {', '.join(allowed_roles)}"}), 400

        query = """
            INSERT INTO users (
                name, contact_number, password_hash, role,
                aanganwaadi_id, gram, block, tehsil, zila
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            name, contact_number, password_hash, role,
            aanganwaadi_id, gram, block, tehsil, zila
        )

        db.execute(query, values)

        new_user_id = db.cursor.lastrowid

        return jsonify({
            "success": True,
            "message": "User registered successfully",
            "user_id": new_user_id
        }), 201

    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f'Database error: {err}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Internal server error: {e}'}), 500
    finally:
        db.close()

@app.route('/search', methods=['GET'])
def search_families():
    db = Database(database=database_name)

    search_query = request.args.get('query', '').strip()

    query = """
        SELECT
            id,
            name AS childName,
            guardian_name AS parentName,
            mobile AS mobileNumber,
            address AS village,
            (plant_photo IS NOT NULL) AS plantDistributed
        FROM
            students
        WHERE 1=1
    """
    params = []

    if search_query:
        search_pattern = f"%{search_query}%"
        query += """
            AND (
                name LIKE %s OR
                mobile LIKE %s
            )
        """
        params.extend([search_pattern, search_pattern])

    try:
        db.execute(query, tuple(params))
        students = db.fetchall()

        formatted_students = []
        for student in students:
            student['plantDistributed'] = bool(student['plantDistributed'])
            formatted_students.append(student)

        return jsonify(formatted_students), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
    finally:
        db.close()

@app.route('/data', methods=['GET'])
def show_all_students():
    db = Database(database=database_name)
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

@app.route('/data1', methods=['GET'])
def show_all_users():
    db = Database(database=database_name)
    result = db.execute("SELECT * FROM users")
    users = db.fetchall()

    table_headers = users[0].keys() if users else []
    html = """
    <html>
    <head>
        <title>All User Data</title>
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

    for row in users:
        html += "<tr>" + "".join(f"<td>{row[col]}</td>" for col in table_headers) + "</tr>"

    html += """
        </table>
    </body>
    </html>
    """

    return Response(html, mimetype='text/html')

@app.route('/upload_plant_photo', methods=['POST'])
def upload_plant_photo():
    if 'photo' not in request.files:
        return jsonify({'message': 'No photo part in the request'}), 400

    photo = request.files['photo']
    username = request.form.get('username')
    name = request.form.get('name')
    plant_stage = request.form.get('plant_stage')
    description = request.form.get('description', '')

    if photo.filename == '':
        return jsonify({'message': 'No selected photo file'}), 400

    if not all([username, name, plant_stage]):
        return jsonify({'message': 'Missing user information or plant stage'}), 400

    db = Database(database=database_name)
    try:
        query_select = "SELECT plant_photo, totalImagesYet FROM students WHERE username = %s AND name = %s"
        db.execute(query_select, (username, name))
        student_data = db.fetchone()

        file_path_to_save_abs = None
        relative_file_path_for_db = None
        current_image_count = 0

        if student_data:
            existing_plant_photo_path_db = student_data.get('plant_photo')
            current_image_count = student_data.get('totalImagesYet', 0)

            if existing_plant_photo_path_db:
                file_path_to_save_abs = os.path.join(UPLOAD_FOLDER, existing_plant_photo_path_db)
                relative_file_path_for_db = existing_plant_photo_path_db
            else:
                filename_base = f"{secure_filename(username)}_{secure_filename(name)}_plant"
                file_extension = os.path.splitext(photo.filename)[1].lower()
                stable_filename = f"{filename_base}{file_extension}"

                file_path_to_save_abs = os.path.join(UPLOAD_FOLDER, stable_filename)
                relative_file_path_for_db = stable_filename
        else:
            return jsonify({'message': 'Student with provided username and name not found.'}), 404

        photo.save(file_path_to_save_abs)

        prediction_message = "मोरिंगा पौधे की तस्वीर सफलतापूर्वक अपलोड और अपडेट की गई।"
        raw_prediction_class = None
        confidence_score = None
        is_moringa_boolean = None

        try:
            image_predictor = ImagePredict()
            raw_prediction_class, confidence_score = image_predictor.imagePredictor(file_path_to_save_abs)

            is_moringa_boolean = (raw_prediction_class == "MUNGA")

            if not is_moringa_boolean:
                prediction_message = "यह मोरिंगा पौधा नहीं लगता है। कृपया सुनिश्चित करें कि आप सही पौधे की तस्वीर अपलोड कर रहे हैं।"

        except Exception as e:
            prediction_message = "फोटो अपलोड हो गई है, लेकिन पौधे की पहचान नहीं हो पाई।"
            is_moringa_boolean = None
            confidence_score = None

        updated_image_count = current_image_count + 1

        query_update = """
        UPDATE students
        SET
            plant_photo = %s,
            totalImagesYet = %s
        WHERE username = %s AND name = %s
        """

        db.execute(query_update, (
            relative_file_path_for_db,
            updated_image_count,
            username,
            name
        ))

        photo_url_for_frontend = f"{request.url_root.strip('/')}{app.static_url_path}/{relative_file_path_for_db}"

        return jsonify({
            'success': True,
            'message': prediction_message,
            'photo_url': photo_url_for_frontend,
            'total_images_uploaded': updated_image_count,
            'is_moringa': is_moringa_boolean,
            'confidence': confidence_score
        }), 200

    except mysql.connector.Error as db_err:
        return jsonify({'message': f'Database error: {str(db_err)}'}), 500
    except Exception as e:
        return jsonify({'message': f'An unexpected error occurred: {str(e)}'}), 500
    finally:
        db.close()

@app.route('/register', methods=['POST'])
def register():
    db = Database(database=database_name)

    try:
        username = request.form.get('username')
        name = request.form.get('name')
        password = request.form.get('username')
        guardian_name = request.form.get('guardian_name')
        father_name = request.form.get('father_name')
        mother_name = request.form.get('mother_name')
        age = request.form.get('age')
        dob = request.form.get('dob')
        aanganwadi_code = request.form.get('aanganwadi_code')
        weight = request.form.get('weight')
        height = request.form.get('height')
        health_status = request.form.get('health_status')

        address = request.form.get('address', '')

        plant_file = request.files.get('plant_photo')
        pledge_file = request.files.get('pledge_photo')

        plant_filename = None
        pledge_filename = None

        totalImagesYet=1

        if plant_file:
            original_filename = secure_filename(plant_file.filename)
            unique_filename = str(uuid.uuid4()) + os.path.splitext(original_filename)[1]
            plant_file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
            plant_filename = unique_filename

        if pledge_file:
            original_filename = secure_filename(pledge_file.filename)
            unique_filename = str(uuid.uuid4()) + os.path.splitext(original_filename)[1]
            pledge_file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
            pledge_filename = unique_filename

        query = """
            INSERT INTO students (
                username, name, password, guardian_name, father_name, mother_name,
                age, dob, aanganwadi_code, weight, height, health_status,
                plant_photo, pledge_photo, address, totalImagesYet, mobile
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            username, name, password, guardian_name, father_name, mother_name,
            int(age),
            dob,
            int(aanganwadi_code),
            float(weight),
            float(height),
            health_status,
            plant_filename,
            pledge_filename,
            address,
            totalImagesYet,
            username
        )
        db.execute(query, values)
        return jsonify({'success': True, 'msg': 'Student registered successfully'}), 201

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    db = Database(database=database_name)

    user_query = "SELECT * FROM users WHERE contact_number = %s AND password_hash = %s"
    db.execute(user_query, (username, password))
    user = db.fetchone()
    if user:
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
                "role": mapped_role,
                "aanganwaadi_id" : user.get("aanganwaadi_id"),
                "address": user.get("gram"),
                "supervisor_name": user.get("supervisor_name")
            },
            "role": mapped_role
        }), 200

    student_query = "SELECT * FROM students WHERE username = %s AND password = %s"
    db.execute(student_query, (username, password))
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

@app.route('/get_photo', methods=['POST'])
def get_photo():
    db = Database(database=database_name)
    mobile = request.form.get('mobile')

    query = "SELECT plant_photo FROM students WHERE mobile = %s"
    db.execute(query, (mobile,))
    result = db.fetchone()

    if result and 'plant_photo' in result and result['plant_photo']:
        photo_path = result['plant_photo']
        return send_from_directory(UPLOAD_FOLDER, photo_path)

    return jsonify({"error": "Photo not found or invalid request"}), 404

@app.route('/check_photo_using_ai', methods=['POST'])
def check_photo_using_ai():
    if 'photo' not in request.files:
        return jsonify({'message': 'No photo part in the request'}), 400

    photo = request.files['photo']

    if photo.filename == '':
        return jsonify({'message': 'No selected photo file'}), 400

    temp_filename = secure_filename(photo.filename)
    temp_filepath = os.path.join(UPLOAD_FOLDER, temp_filename)
    photo.save(temp_filepath)

    try:
        image_predictor = ImagePredict()
        class_predicted, confidence = image_predictor.imagePredictor(temp_filepath)

        os.remove(temp_filepath)

        return jsonify({
            'class_predicted': class_predicted,
            'confidence': confidence
        }), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)