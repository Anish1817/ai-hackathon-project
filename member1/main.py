# from fastapi import FastAPI, UploadFile, File
# import shutil
# import os
# import json
# from exif_utils import extract_metadata
# from database import init_db, insert_image, fetch_all

# app = FastAPI()

# UPLOAD_DIR = "uploads"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# init_db()


# @app.post("/upload/")
# async def upload_image(file: UploadFile = File(...)):
#     file_path = os.path.join(UPLOAD_DIR, file.filename)

#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     metadata = extract_metadata(file_path)

#     if not metadata:
#         return {"error": "No valid EXIF GPS/timestamp data found"}

#     result = {
#         "image_id": file.filename,
#         "lat": metadata["lat"],
#         "lon": metadata["lon"],
#         "timestamp": metadata["timestamp"]
#     }

#     insert_image(result)

#     return result


# @app.get("/export/")
# def export_data():
#     rows = fetch_all()

#     data = []
#     for row in rows:
#         data.append({
#             "image_id": row[0],
#             "lat": row[1],
#             "lon": row[2],
#             "timestamp": row[3]
#         })

#     with open("output_data.json", "w") as f:
#         json.dump(data, f, indent=4)

#     return {
#         "message": "Exported successfully",
#         "total_records": len(data)
#     }

import os
import json
from exif_utils import extract_metadata
from database import insert_image, fetch_all

def process_folder(folder_path="images"):
    
    if not os.path.exists(folder_path):
        print("Folder not found.")
        return
    else :
        print("found")
    files = os.listdir(folder_path)

    valid = 0
    invalid = 0

    for file in files:
        file_path = os.path.join(folder_path, file)

        if not file.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        # metadata = extract_metadata(file_path)
        metadata = extract_metadata(file_path)

        print(f"\nProcessing: {file}")
        print("Metadata returned:", metadata)
        if not metadata:
            invalid += 1
            continue

        result = {
            "image_id": file,
            "lat": metadata["lat"],
            "lon": metadata["lon"],
            "timestamp": metadata["timestamp"]
        }

        insert_image(result)
        valid += 1

    print(f"Processed: {valid + invalid}")
    print(f"Valid: {valid}")
    print(f"Invalid: {invalid}")

    export_json()


def export_json():
    rows = fetch_all()

    data = []
    for row in rows:
        data.append({
            "image_id": row[0],
            "lat": row[1],
            "lon": row[2],
            "timestamp": row[3]
        })

    with open("output_data.json", "w") as f:
        json.dump(data, f, indent=4)

    print("output_data.json generated successfully")


process_folder()




