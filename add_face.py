import cv2
import pickle
import numpy as np
import os

# Create the 'data/' directory if it doesn't exist
if not os.path.exists('data/'):
    os.makedirs('data/')

# Initialize the video capture
video = cv2.VideoCapture(0)  # Change index if needed
if not video.isOpened():
    print("Error: Camera not accessible.")
    exit()

facedetect = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

faces_data = []
i = 0
name = input("Enter your roll number: ")
framesTotal = 51
captureAfterFrame = 2

while True:
    ret, frame = video.read()
    if not ret:
        print("Error: Could not read frame from camera.")
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w]
        resized_img = cv2.resize(crop_img, (50, 50))

        # Append face data every 'captureAfterFrame' frames
        if len(faces_data) < framesTotal and i % captureAfterFrame == 0:
            faces_data.append(resized_img)

        i += 1

        cv2.putText(frame, str(len(faces_data)), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 1)

    cv2.imshow('frame', frame)
    k = cv2.waitKey(1)

    # Exit when 'q' is pressed or data collection is complete
    if k == ord('q') or len(faces_data) >= framesTotal:
        break

# Release resources
video.release()
cv2.destroyAllWindows()

# Ensure faces_data is not empty
if len(faces_data) == 0:
    print("Error: No face data captured.")
    exit()

# Convert face data to a NumPy array
faces_data = np.asarray(faces_data)
faces_data = faces_data.reshape((faces_data.shape[0], -1))
print(faces_data)

# Save names and faces data
if 'names.pkl' not in os.listdir('data/'):
    names = [name] * framesTotal
    with open('data/names.pkl', 'wb') as f:
        pickle.dump(names, f)
else:
    with open('data/names.pkl', 'rb') as f:
        names = pickle.load(f)
    names = names + [name] * framesTotal
    with open('data/names.pkl', 'wb') as f:
        pickle.dump(names, f)

if 'faces_data.pkl' not in os.listdir('data/'):
    with open('data/faces_data.pkl', 'wb') as f:
        pickle.dump(faces_data, f)
else:
    with open('data/faces_data.pkl', 'rb') as f:
        faces = pickle.load(f)
    faces = np.append(faces, faces_data, axis=0)
    with open('data/faces_data.pkl', 'wb') as f:
        pickle.dump(faces, f)