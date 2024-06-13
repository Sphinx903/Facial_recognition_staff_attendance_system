from flask import Flask, request, jsonify
from flask_cors import CORS
import face_recognition
import numpy as np
import cv2
import sqlite3
from datetime import datetime, date
import base64

app = Flask(__name__)
CORS(app)

# Initialize the database
def init_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Load known faces
known_face_encodings = []
known_face_names = []

def load_known_faces():
    try:
        print("Loading known faces...")
        image = face_recognition.load_image_file("images/staff1.png")
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append("Antonio")
            print("Loaded face for Staff1.")
        else:
            print("No face found in staff1.jpg")
        
        image = face_recognition.load_image_file("images/staff1.png")
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append("Staff2 Name")
            print("Loaded face for Staff2.")
        else:
            print("No face found in staff2.jpg")

        # Add more staff members as needed

    except FileNotFoundError as e:
        print(f"Error: {e}")

# Log attendance
def log_attendance(name):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)", 
              (name, str(date.today()), str(datetime.now().time())))
    conn.commit()
    conn.close()

# Endpoint to process video frame and recognize face
@app.route('/recognize', methods=['POST'])
def recognize():
    data = request.json
    if 'image' not in data:
        return jsonify({"error": "No image data"}), 400

    img_data = base64.b64decode(data['image'])
    np_img = np.frombuffer(img_data, dtype=np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    rgb_frame = frame[:, :, ::-1]

    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    recognized_names = []

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            log_attendance(name)
            recognized_names.append(name)

    return jsonify({"recognized": recognized_names})

if __name__ == "__main__":
    init_db()
    load_known_faces()
    app.run(host='0.0.0.0', port=5000)
