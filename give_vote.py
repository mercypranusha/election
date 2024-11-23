import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from win32com.client import Dispatch
from sklearn.neighbors import KNeighborsClassifier

def speak(message):
    """Convert text to speech."""
    speaker = Dispatch("SAPI.SpVoice")
    speaker.Speak(message)

def load_data():
    """Load names and face data from pickle files."""
    with open('data/names.pkl', 'rb') as f:
        labels = pickle.load(f)
    with open('data/faces_data.pkl', 'rb') as f:
        faces = pickle.load(f)
    return labels, faces

def initialize_video_capture():
    """Initialize video capture and return the video object."""
    video = cv2.VideoCapture(0)
    if not video.isOpened():
        raise RuntimeError("Error: Could not open video capture.")
    return video

def check_if_exists(value):
    """Check if a voter has already voted."""
    try:
        with open("Votes.csv", "r") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row and row[0] == value:
                    print(f"Found existing vote for: {value}")  # Debugging output
                    return True
    except FileNotFoundError:
        print("Votes.csv not found or unable to open.")
    return False

def record_vote(output, vote):
    """Record a vote in the CSV file."""
    speak("YOUR VOTE HAS BEEN RECORDED")
    time.sleep(1)
    
    timestamp = datetime.now()
    date_str = timestamp.strftime("%d-%m-%Y")
    time_str = timestamp.strftime("%H:%M:%S")
    
    with open("Votes.csv", "a", newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not os.path.isfile("Votes.csv"):
            writer.writerow(['ROLL NO.', 'VOTE', 'DATE', 'TIME'])  # Write header if file is new
        writer.writerow([output[0], vote, date_str, time_str])
    
    speak("THANK YOU FOR ELECTING YOUR CR")

def main():
    print("Starting the voting system...")
    
    # Load labels and faces data
    LABELS, FACES = load_data()
    
    # Initialize KNN classifier
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(FACES, LABELS)

    # Initialize video capture
    video = initialize_video_capture()

    # Load Haar Cascade for face detection
    facedetect = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Load background image
    imgBackground = cv2.imread("background.png")
    if imgBackground is None:
        raise FileNotFoundError("Error: 'background.png' not found. Please check the file path.")

    bg_height, bg_width, _ = imgBackground.shape
    frame_width, frame_height = 480, 480

    # Resize background if necessary
    if bg_height < 110 + frame_height or bg_width < 50 + frame_width:
        imgBackground = cv2.resize(imgBackground, (max(bg_width, 50 + frame_width), max(bg_height, 110 + frame_height)))
        bg_height, bg_width, _ = imgBackground.shape

    while True:
        ret, frame = video.read()
        if not ret:
            print("Failed to capture video.")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = facedetect.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        output = None
        
        for (x, y, w, h) in faces:
            crop_img = frame[y:y+h, x:x+w]
            resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)
            
            try:
                output = knn.predict(resized_img)
            except Exception as e:
                print(f"Prediction error: {e}")
                output = None

            # Check if the face belongs to known data
            if output is not None and output[0] in LABELS:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 255), 2)
                cv2.rectangle(frame, (x, y - 40), (x + w, y), (50, 50, 255), -1)
                cv2.putText(frame, str(output[0]), (x, y - 15), cv2.FONT_HERSHEY_COMPLEX, 1,
                            (255, 255, 255), 1)

                if bg_height >= 110 + frame_height and bg_width >= 50 + frame_width:
                    frame_resized = cv2.resize(frame, (frame_width, frame_height))
                    imgBackground[110:110 + frame_height, 50:50 + frame_width] = frame_resized

                cv2.imshow('frame', imgBackground)

                # Check if the voter has already voted
                voter_exist = check_if_exists(output[0])
                if voter_exist:
                    print(f"YOU HAVE ALREADY VOTED: {output[0]}")  # Debugging output
                    speak("YOU HAVE ALREADY VOTED")
                    break

                k = cv2.waitKey(1)

                # Voting options based on key presses
                if k == ord('1'):
                    record_vote(output, "clock")
                    break
                elif k == ord('2'):
                    record_vote(output, "boat")
                    break
                elif k == ord('3'):
                    record_vote(output, "apple")
                    break

            else:
                print("YOU DO NOT BELONG TO THIS BRANCH")
                speak("YOU DO NOT BELONG TO THIS BRANCH")
                break

        if output is None or output[0] not in LABELS:
            break

    video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        main()
        input("Press Enter to exit...")  # Keep console open until Enter is pressed
    except Exception as e:
        print(f"An error occurred: {e}")