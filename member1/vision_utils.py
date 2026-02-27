from google.cloud import vision
from google.oauth2 import service_account
import os

BASE_DIR = os.path.dirname(__file__)
KEY_PATH = os.path.join(BASE_DIR, "vision-key.json")

def get_vision_client():
    credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
    return vision.ImageAnnotatorClient(credentials=credentials)

def get_location_from_image(image_path):
    client = get_vision_client()

    with open(image_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.landmark_detection(image=image)

    if response.landmark_annotations:
        landmark = response.landmark_annotations[0]
        if landmark.locations:
            lat = landmark.locations[0].lat_lng.latitude
            lon = landmark.locations[0].lat_lng.longitude
            return lat, lon

    return None