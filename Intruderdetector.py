import face_recognition
import cv2
import smtplib
import ssl
import os
from email.message import EmailMessage
import time

# Email Configuration
EMAIL_SENDER = ""  # Replace with your email
EMAIL_PASSWORD = ""  # Replace with your app password
EMAIL_RECEIVER = ""  # Your email for notifications
# EMAIL_RECEIVERS = ["", "another_email@gmail.com"]  

# Load known face encodings and names
known_face_encodings = []
known_face_names = []

for name, img_path in [("Name1", r"File path"),
                       ("Name2", r"File path")]:
    image = face_recognition.load_image_file(img_path)
    known_face_encodings.append(face_recognition.face_encodings(image)[0])
    known_face_names.append(name)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)
    face_locations = face_recognition.face_locations(small_frame)
    face_encodings = face_recognition.face_encodings(small_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
        face_names.append(name)

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(frame, name, (left + 6, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
        
        if name == "Unknown":
            image_path = "intruder.jpg"
            cv2.imwrite(image_path, frame)
            
            # Send Email with Intruder Image
            msg = EmailMessage()
            msg['Subject'] = "Intruder Alert!"
            msg['From'] = EMAIL_SENDER
            msg['To'] = EMAIL_RECEIVER  # Change this to EMAIL_RECEIVERS if using multiple
            msg.set_content("An unrecognized person was detected! See the attached image.")
            
            with open(image_path, 'rb') as img:
                msg.add_attachment(img.read(), maintype='image', subtype='jpeg', filename="intruder.jpg")
            
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                    server.send_message(msg)
                print("Intruder alert email sent successfully!")
            except Exception as e:
                print(f"Failed to send email: {e}")
            
    cv2.imshow("Video Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

