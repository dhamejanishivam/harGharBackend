from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from flask import Response
import uuid # Import uuid for unique IDs
import os
from werkzeug.utils import secure_filename
import uuid # Import uuid for unique IDs
import datetime # Add this import at the top of your file
import model
from datetime import datetime # Import datetime specifically


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# https://grx6djfl-5000.inc1.devtunnels.ms/
# https://grx6djfl-5001.inc1.devtunnels.ms/


"""
curl -X POST https://grx6djfl-5001.inc1.devtunnels.ms/login \
-H "Content-Type: application/json" \
-d '{"username": "CGAB001", "password": "hgm@2025"}'
"""


class ImagePredict:
    def __init__(self):
        self.aiObject = model.IMAGECLASSIFIER()
    def imagePredictor(self,image_path):
        result = self.aiObject.predict(image_path)
        classPredicted=result[0] # 1=Munga 0=NotMunga
        confidence=result[1]
        return classPredicted,confidence

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
            print(f"==========DEBUG: Query committed successfully: {query}")
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


"""
    1. Name of anaganbadi
    2. Location of anaganbadi
    3. Village name of anaganbadi ()
"""


# Load the database here
users={
    'CGCO001':'hgm@2025',
    'CGAB001':'hgm@2025',
    'CGPV001':'hgm@2025',
}



@app.route('/')
def homepage():
    return '<body style=background-color:black;color:white;display:flex;align-items:center;justify-content:center;font-size:40px;>WORKING'



@app.route('/search2')
def search2Results():
    db = Database(database="project")
    try:
        # Query 1: Total entries in students table
        query_total_students = "SELECT COUNT(*) AS total_students FROM students"
        db.execute(query_total_students)
        total_students_result = db.fetchone()
        total_students = total_students_result['total_students'] if total_students_result else 0

        # Query 2: Sum of all entries of column totalImagesYet
        query_total_images = "SELECT SUM(totalImagesYet) AS total_images_uploaded FROM students"
        db.execute(query_total_images)
        total_images_result = db.fetchone()
        # SUM can return NULL if there are no rows, so handle that case
        total_images_uploaded = total_images_result['total_images_uploaded'] if total_images_result and total_images_result['total_images_uploaded'] is not None else 0

        # Query 3: Name of the latest entry
        # We order by 'id' in descending order to get the latest entry (assuming ID is auto-incrementing and indicates creation order)
        # and LIMIT 1 to get only the single most recent one.
        query_latest_student_name = "SELECT name FROM students ORDER BY id DESC LIMIT 1"
        db.execute(query_latest_student_name)
        latest_student_result = db.fetchone()
        # Extract the name, or set to None if no students exist
        latest_student_name = latest_student_result['name'] if latest_student_result else None


        print(f"[INFO] SEARCH_2 EXECUTED")
        # print(f"[INFO] Fetched total images uploaded: {total_images_uploaded}")
        return jsonify({
            "success": True,
            "total_students": total_students,
            "total_images_uploaded": total_images_uploaded,
            "latest_student_name": latest_student_name # Added this line
        }), 200
    

    except Exception as e:
        print(f"[SEARCH2 ERROR] {e}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
    finally:
        db.close()




@app.route('/families/user/<string:user_id>', methods=['GET'])
def get_family_by_user_id(user_id):
    """
    Fetches student/family data based on the provided username (which is user_id here).
    This endpoint corresponds to apiService.getFamilyByUserId in the frontend.
    """
    db = Database(database="project") # Get a new DB connection for this request
    try:
        # Assuming 'user_id' from the URL maps directly to the 'username' column in your students table
        query = """
            SELECT
                id,
                username,
                name AS childName,
                guardian_name AS parentName, -- Or motherName/fatherName based on preference
                mother_name AS motherName,
                father_name AS fatherName,
                -- Assuming username is used for mobileNumber
                username AS mobileNumber, 
                address AS village, -- 'address' is a combined field in your DB, mapped to village
                age,
                dob AS dateOfBirth,
                weight,
                height,
                aanganwadi_code AS anganwadiCode, -- Ensure consistency in naming
                plant_photo, -- The stored path to the plant photo
                pledge_photo, -- The stored path to the pledge photo
                totalImagesYet,
                -- You might also want to include centerName, workerName if available in 'students' or by joining
                -- For now, just pulling directly from 'students' table
                'active' as status -- Assuming all fetched families are active for now, or fetch from DB
            FROM
                students
            WHERE
                username = %s
        """
        db.execute(query, (user_id,))
        family_data = db.fetchone()

        if family_data:
            # Convert plant_photo and pledge_photo to full URLs if they exist
            # Assumes your Flask app serves static files from the UPLOAD_FOLDER under /static/plant_photos
            if family_data.get('plant_photo'):
                family_data['plant_photo'] = f"{request.url_root.strip('/')}{app.static_url_path}/{family_data['plant_photo']}"
            if family_data.get('pledge_photo'):
                family_data['pledge_photo'] = f"{request.url_root.strip('/')}{app.static_url_path}/{family_data['pledge_photo']}"
            
            # Ensure totalImagesYet is an integer (it usually comes as an int but good to be explicit)
            family_data['totalImagesYet'] = int(family_data.get('totalImagesYet', 0))

            print(f"[INFO] Family data for user_id '{user_id}' fetched successfully.")
            return jsonify(family_data), 200
        else:
            print(f"[INFO] No family data found for user_id '{user_id}'.")
            return jsonify({'message': 'Family data not found for this user.'}), 404

    except mysql.connector.Error as db_err:
        print(f"[GET FAMILY BY USER ID DB ERROR] {db_err}")
        return jsonify({'error': 'Database error', 'message': str(db_err)}), 500
    except Exception as e:
        print(f"[GET FAMILY BY USER ID ERROR] {e}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
    finally:
        db.close() # Always close the DB connection






@app.route('/searchAng', methods=['GET'])
def searchAng():
    db = Database(database="project")
    try:
        # Fetch all columns and all rows from the users table
        query = "SELECT id, name, contact_number, role, created_at, aanganwaadi_id, gram, block, tehsil, zila FROM users"
        db.execute(query)
        users_data = db.fetchall()

        # IMPORTANT: Do not expose password_hash to the frontend.
        # The query above explicitly selects only the safe columns.

        if users_data:
            print("[INFO] All users data fetched successfully.")
            return jsonify(users_data), 200
        else:
            print("[INFO] No users found in the database.")
            return jsonify([]), 200 # Return an empty array if no users

    except Exception as e:
        print(f"[SEARCHANG ERROR] {e}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
    finally:
        db.close()



@app.route('/registerAng', methods=['POST'])
def registerAng():
    db = Database(database="project")
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "message": "No JSON data provided"}), 400

        # Extract fields directly from the JSON data
        name = data.get('name')
        contact_number = data.get('contact_number')
        password_hash = data.get('password_hash') # Expecting hashed password from frontend
        role = data.get('role')
        aanganwaadi_id = data.get('aanganwaadi_id')
        gram = data.get('gram')
        block = data.get('block')
        tehsil = data.get('tehsil')
        zila = data.get('zila')

        # Basic validation (add more robust validation as needed)
        if not all([name, contact_number, password_hash, role]):
            return jsonify({"success": False, "message": "Missing required fields (name, contact_number, password_hash, role)"}), 400
        
        # Validate role against allowed enum values
        allowed_roles = ['admin', 'aanganwadi_worker', 'health_worker']
        if role not in allowed_roles:
            return jsonify({"success": False, "message": f"Invalid role: {role}. Allowed roles are {', '.join(allowed_roles)}"}), 400

        # Insert data into the users table
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
        
        # Get the ID of the newly inserted user
        new_user_id = db.cursor.lastrowid

        print(f"[INFO] New user registered: {name} (ID: {new_user_id})")
        return jsonify({
            "success": True,
            "message": "User registered successfully",
            "user_id": new_user_id
        }), 201

    except mysql.connector.Error as err:
        print(f"[REGISTERANG DB ERROR] {err}")
        return jsonify({'success': False, 'message': f'Database error: {err}'}), 500
    except Exception as e:
        print(f"[REGISTERANG ERROR] {e}")
        return jsonify({'success': False, 'message': f'Internal server error: {e}'}), 500
    finally:
        db.close()




@app.route('/search', methods=['GET'])
def search_families():
    db = Database(database="project") 
    
    search_query = request.args.get('query', '').strip()
    
    print(f"\n--- DEBUGGING SEARCH ---")
    print(f"Received query: '{search_query}'")

    query = """
        SELECT
            id,
            name AS childName,
            guardian_name AS parentName, 
            username AS mobileNumber,
            address AS village,
            -- DATE_FORMAT(created_at, '%d/%m/%Y') AS registrationDate, -- REMOVED THIS LINE
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
                username LIKE %s
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
        
        print("[INFO] Result for searched fetched succesfully")
        return jsonify(formatted_students), 200

    except Exception as e:
        print(f"[SEARCH ERROR] {e}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
    finally:
        db.close()





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



@app.route('/upload_plant_photo', methods=['POST'])
def upload_plant_photo():
    if 'photo' not in request.files:
        return jsonify({'message': 'No photo part in the request'}), 400
    
    photo = request.files['photo']
    username = request.form.get('username')
    name = request.form.get('name')
    plant_stage = request.form.get('plant_stage')
    description = request.form.get('description', '')

    print(f"Received upload request: Username='{username}', Name='{name}', Stage='{plant_stage}', Description='{description}'")

    if photo.filename == '':
        return jsonify({'message': 'No selected photo file'}), 400
    
    if not all([username, name, plant_stage]):
        return jsonify({'message': 'Missing user information or plant stage'}), 400

    db = Database(database="project")
    try:
        query_select = "SELECT plant_photo, totalImagesYet FROM students WHERE username = %s AND name = %s"
        db.execute(query_select, (username, name))
        student_data = db.fetchone()

        file_path_to_save_abs = None
        relative_file_path_for_db = None
        current_image_count = 0
        print(f"========DEBUG: Fetched current_image_count: {current_image_count} for user {username}, name {name}")

        if student_data:
            existing_plant_photo_path_db = student_data.get('plant_photo')
            current_image_count = student_data.get('totalImagesYet', 0)

            if existing_plant_photo_path_db:
                file_path_to_save_abs = os.path.join(UPLOAD_FOLDER, existing_plant_photo_path_db)
                relative_file_path_for_db = existing_plant_photo_path_db
                print(f"Existing plant photo found in DB. Will overwrite at: {file_path_to_save_abs}")
            else:
                filename_base = f"{secure_filename(username)}_{secure_filename(name)}_plant"
                file_extension = os.path.splitext(photo.filename)[1].lower()
                stable_filename = f"{filename_base}{file_extension}"
                
                file_path_to_save_abs = os.path.join(UPLOAD_FOLDER, stable_filename)
                relative_file_path_for_db = stable_filename
                print(f"No existing plant photo in DB. Generating new stable file at: {file_path_to_save_abs}")
        else:
            print(f"Error: Student with username '{username}' and name '{name}' not found.")
            return jsonify({'message': 'Student with provided username and name not found.'}), 404
        
        photo.save(file_path_to_save_abs)
        print(f"Photo saved successfully to: {file_path_to_save_abs}")

        # --- Image Classification ---
        prediction_message = "मोरिंगा पौधे की तस्वीर सफलतापूर्वक अपलोड और अपडेट की गई।" # Default success message
        raw_prediction_class = None # Will store 0 or 1 from ImagePredict
        confidence_score = None
        is_moringa_boolean = None # Will store True/False based on raw_prediction_class

        try:
            image_predictor = ImagePredict()
            raw_prediction_class, confidence_score = image_predictor.imagePredictor(file_path_to_save_abs)
            
            # Convert raw_prediction_class (0 or 1) to a boolean
            is_moringa_boolean = (raw_prediction_class == 1) 
            
            print(f"Image prediction: Raw Class='{raw_prediction_class}' (Is Moringa? {is_moringa_boolean}) with confidence {confidence_score}")

            # --- Apply your conditional message logic here ---
            if not is_moringa_boolean: # If prediction is 0 (meaning False for moringa)
                prediction_message = "यह मोरिंगा पौधा नहीं लगता है। कृपया सुनिश्चित करें कि आप सही पौधे की तस्वीर अपलोड कर रहे हैं।" # "This doesn't seem to be a moringa plant. Please ensure you are uploading a photo of the correct plant."
            # else, it remains the default success message

        except Exception as e:
            print(f"Warning: Image prediction failed: {e}")
            prediction_message = "फोटो अपलोड हो गई है, लेकिन पौधे की पहचान नहीं हो पाई।" # "Photo uploaded, but plant identification failed."
            is_moringa_boolean = None # Set to None if prediction fails
            confidence_score = None

       # 3. Update the students table
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
        
        print(f"Database updated for {username} with new photo path '{relative_file_path_for_db}' and image count: {updated_image_count}")

        photo_url_for_frontend = f"{request.url_root.strip('/')}{app.static_url_path}/{relative_file_path_for_db}"
        print(f"Photo URL for frontend: {photo_url_for_frontend}")

        return jsonify({
            'success': True, # Still true because photo is saved and DB updated
            'message': prediction_message, # This is the dynamic message
            'photo_url': photo_url_for_frontend,
            'total_images_uploaded': updated_image_count,
            'is_moringa': is_moringa_boolean, # Send the boolean prediction (True/False/None)
            'confidence': confidence_score # Send the confidence
        }), 200

    except mysql.connector.Error as db_err:
        print(f"Database error during photo upload: {db_err}")
        return jsonify({'message': f'Database error: {str(db_err)}'}), 500
    except Exception as e:
        print(f"Error during photo upload: {e}")
        return jsonify({'message': f'An unexpected error occurred: {str(e)}'}), 500
    finally:
        db.close()





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
    app.run(debug=True,port=5001)