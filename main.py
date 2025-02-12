import os
from fastapi import FastAPI, Query
import face_recognition
import requests
import numpy as np
import cv2
import urllib.parse

app = FastAPI()

def download_image(url):
    url = urllib.parse.unquote(url)
    response = requests.get(url)
    if response.status_code == 200:
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        return cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return None

def get_face_encoding(image):
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image)
    if len(face_locations) == 0:
        return None
    encodings = face_recognition.face_encodings(rgb_image, face_locations)
    return encodings[0] if len(encodings) > 0 else None

@app.get("/compare_faces/")
def compare_faces(image1_url: str = Query(...), image2_url: str = Query(...)):
    try:
        image1 = download_image(image1_url)
        image2 = download_image(image2_url)

        if image1 is None or image2 is None:
            return {"success": False, "message": "Failed to load one or both images"}

        encoding1 = get_face_encoding(image1)
        encoding2 = get_face_encoding(image2)

        if encoding1 is None or encoding2 is None:
            return {"success": False, "message": "No face detected in one or both images"}

        match = bool(face_recognition.compare_faces([encoding1], encoding2)[0])

        return {"success": True, "match": match}

    except Exception as e:
        return {"success": False, "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
