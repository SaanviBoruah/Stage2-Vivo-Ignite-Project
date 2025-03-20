import streamlit as st
import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2
import numpy as np
from fer import FER

# Set up the app
st.set_page_config(page_title="Real-time Emotion Detection", layout="wide")
st.title("🎭 Real-time Facial Emotion Detection")

# Initialize detector
detector = FER()

# Webcam input
img_file_buffer = st.camera_input("Take a picture for emotion analysis")

if img_file_buffer is not None:
    # Convert buffer to OpenCV format
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    # Detect emotions
    results = detector.detect_emotions(cv2_img)
    
    # Draw results
    for face in results:
        x, y, w, h = face["box"]
        emotions = face["emotions"]
        dominant_emotion = max(emotions, key=emotions.get)
        confidence = emotions[dominant_emotion]
        
        # Draw rectangle and text
        cv2.rectangle(cv2_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(cv2_img, 
                   f"{dominant_emotion} ({confidence:.0%})", 
                   (x, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   0.9, (0,255,0), 2)
    
    # Display processed image
    st.image(cv2_img, channels="BGR", caption="Processed Image")
    
    # Show detailed emotions
    st.subheader("Emotion Analysis Results")
    if results:
        for i, face in enumerate(results):
            st.write(f"**Face {i+1}**")
            for emotion, score in face["emotions"].items():
                st.progress(score, text=f"{emotion.capitalize()}: {score:.2%}")
    else:
        st.warning("No faces detected in the image")
