import cv2
from fer import FER
import random
import webbrowser
import time  # To manage time-based capturing

# Initialize the webcam and FER emotion detector
cap = cv2.VideoCapture(0)  # 0 is for the default camera
detector = FER()

# Store face data: age estimates, look comments, emotion consistency, and song suggestion
face_data = {}
start_time = time.time()  # Track the starting time for stabilization
song_played = False  # To ensure only one song is played

# Function to estimate age based on face box size (simplified)
def estimate_age(face_box):
    (x, y, w, h) = face_box
    face_area = w * h
    if face_area > 50000:
        return random.randint(25, 45)  # Adult
    elif face_area > 30000:
        return random.randint(18, 25)  # Young Adult
    else:
        return random.randint(12, 18)  # Teenager

# Function to categorize generation based on age
def categorize_generation(age):
    if age <= 24:
        return "Gen Z"
    elif age <= 40:
        return "Millennial"
    elif age <= 56:
        return "Gen X"
    else:
        return "Boomer"

# Function to give a stable, random comment on appearance
def assign_stable_look():
    looks_comments = ["Appealing", "Handsome", "Beautiful", "Pretty", "Dashing", "Charming", "Elegant", "Stunning", "Graceful", "Radiant"]
    return random.choice(looks_comments)

# Function to suggest songs based on emotion, generation, and age
def suggest_song(emotion, generation, age):
    # Song suggestion database
    song_database = {
        "Gen Z": {
            "happy": ("Blinding Lights - The Weeknd", "https://www.youtube.com/watch?v=4NRXx6U8ABQ"),
            "sad": ("Someone You Loved - Lewis Capaldi", "https://www.youtube.com/watch?v=bCuhuePlP8o"),
            "angry": ("bad guy - Billie Eilish", "https://www.youtube.com/watch?v=DyDfgMOUjCI"),
            "neutral": ("Levitating - Dua Lipa", "https://www.youtube.com/watch?v=TUVcZfQe-Kw")
        },
        "Millennial": {
            "happy": ("Uptown Funk - Mark Ronson ft. Bruno Mars", "https://www.youtube.com/watch?v=OPf0YbXqDm0"),
            "sad": ("Fix You - Coldplay", "https://www.youtube.com/watch?v=k4V3Mo61fJM"),
            "angry": ("Rolling in the Deep - Adele", "https://www.youtube.com/watch?v=rYEDA3JcQqw"),
            "neutral": ("Happy - Pharrell Williams", "https://www.youtube.com/watch?v=ZbZSe6N_BXs")
        },
        "Gen X": {
            "happy": ("Don't Stop Believin' - Journey", "https://www.youtube.com/watch?v=1k8craCGpgs"),
            "sad": ("Tears in Heaven - Eric Clapton", "https://www.youtube.com/watch?v=JxPj3GAYYZ0"),
            "angry": ("Smells Like Teen Spirit - Nirvana", "https://www.youtube.com/watch?v=hTWKbfoikeg"),
            "neutral": ("Take On Me - a-ha", "https://www.youtube.com/watch?v=djV11Xbc914")
        },
        "Boomer": {
            "happy": ("Here Comes The Sun - The Beatles", "https://www.youtube.com/watch?v=KQetemT1sWc"),
            "sad": ("Yesterday - The Beatles", "https://www.youtube.com/watch?v=jo505ZyaCbA"),
            "angry": ("Born to Be Wild - Steppenwolf", "https://www.youtube.com/watch?v=egMWlD3fLJ8"),
            "neutral": ("Hotel California - Eagles", "https://www.youtube.com/watch?v=EqPtz5qN7HM")
        }
    }

    # Select the song based on generation and emotion
    generation_songs = song_database.get(generation, {})
    song_info = generation_songs.get(emotion.lower(), ("Unknown", ""))
    
    return song_info

# Function to stabilize data (fixed duration of stabilization before capturing)
def is_stabilized(duration=4):
    return time.time() - start_time > duration

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    if not ret:
        break
    
    # Use FER to detect emotion in the current frame
    emotions = detector.detect_emotions(frame)
    
    # Draw rectangles around faces and annotate emotions
    for emotion in emotions:
        (x, y, w, h) = emotion["box"]
        face_id = (x, y, w, h)  # Use face box as a temporary ID for the face
        
        # Draw rectangle around face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Get the emotion with the highest score
        dominant_emotion = max(emotion["emotions"], key=emotion["emotions"].get)
        
        # Initialize or update face data (age estimates and look)
        if face_id not in face_data:
            # First detection: assign random look comment and estimated age
            face_data[face_id] = {
                "age": None,  # Age will be set after stabilization
                "emotion": None,  # Emotion will be set after stabilization
                "generation": None,  # Generation will be set after stabilization
                "look": assign_stable_look(),  # Stable look assigned once
                "song_link": None,  # To store the song link
            }
        
        # Stabilize for 4 seconds, then capture and hold the emotion, age, and generation constant
        if is_stabilized() and face_data[face_id]["emotion"] is None:
            # Once stabilized, capture and hold the emotion, age, and generation
            stable_age = estimate_age((x, y, w, h))
            stable_emotion = dominant_emotion
            stable_generation = categorize_generation(stable_age)
            
            # Store the constant data
            face_data[face_id]["age"] = stable_age
            face_data[face_id]["emotion"] = stable_emotion
            face_data[face_id]["generation"] = stable_generation
            
            # Suggest a song if not already suggested and no song has been played yet
            if not song_played:
                song_title, song_link = suggest_song(stable_emotion, stable_generation, stable_age)
                face_data[face_id]["song_link"] = song_link
                # Open YouTube link in browser once
                webbrowser.open(song_link)
                song_played = True  # Ensure only one song is played
        
        # Display stabilized emotion, age, generation, appearance
        if face_data[face_id]["emotion"]:
            stable_age = face_data[face_id]["age"]
            stable_emotion = face_data[face_id]["emotion"]
            stable_generation = face_data[face_id]["generation"]
            look_comment = face_data[face_id]["look"]
            
            cv2.putText(frame, f"Emotion: {stable_emotion}", (x, y - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, f"Age: {stable_age}", (x, y - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, f"Gen: {stable_generation}", (x, y - 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, f"Look: {look_comment}", (x, y - 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
        else:
            # During stabilization phase, display "Emotion Stabilizing..."
            cv2.putText(frame, "Emotion: Stabilizing...", (x, y - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
    
    # Display the resulting frame
    cv2.imshow('Emotion Detection', frame)
    
    # Break the loop when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
