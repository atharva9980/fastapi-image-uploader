import os
import cloudinary
import cloudinary.uploader
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
load_dotenv()

# --- Load configuration from environment variables ---
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
# --- End of configuration ---

app = FastAPI()

# --- START OF THE FIX ---
# Mount the static directory to the "/static" path.
# This is specific and will not conflict with other paths.
app.mount("/static", StaticFiles(directory="static"), name="static")
# --- END OF THE FIX ---

print(f"--- UPLOAD SERVICE: API Key loaded: {CLOUDINARY_API_KEY is not None} ---")

# CORS middleware (no changes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cloudinary config (no changes)
cloudinary.config(
  cloud_name = CLOUDINARY_CLOUD_NAME,
  api_key = CLOUDINARY_API_KEY,
  api_secret = CLOUDINARY_API_SECRET,
  secure = True
)

# --- FIX ---
# This endpoint now serves the HTML from the root path "/"
@app.get("/")
async def serve_uploader_page():
    return FileResponse('uploader.html')
# --- END OF FIX ---

@app.post("/upload-image/")
async def create_upload_file(file: UploadFile = File(...)):
    # This function is correct and needs no changes.
    try:
        print(f"--- UPLOAD SERVICE: Received file: {file.filename} ---")
        contents = await file.read()
        upload_result = cloudinary.uploader.upload(
            contents, folder="craft_id_artworks"
        )
        secure_url = upload_result.get("secure_url")
        if not secure_url:
            raise HTTPException(status_code=500, detail="Cloudinary did not return a URL")
        print(f"--- UPLOAD SERVICE: Success! URL: {secure_url} ---")
        return {"file_url": secure_url}
    except Exception as e:
        print(f"--- UPLOAD SERVICE: Error: {e} ---")
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")