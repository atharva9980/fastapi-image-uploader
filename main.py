import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # <-- NEW: Import StaticFiles
from fastapi.responses import FileResponse   # <-- NEW: Import FileResponse

load_dotenv()

# --- Load configuration from environment variables ---
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# --- FastAPI App Definition ---
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cloudinary config
cloudinary.config(
  cloud_name = CLOUDINARY_CLOUD_NAME,
  api_key = CLOUDINARY_API_KEY,
  api_secret = CLOUDINARY_API_SECRET,
  secure = True
)

# --- THE API ENDPOINT ---
@app.post("/api/upload-image")
async def create_upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        upload_result = cloudinary.uploader.upload(
            contents, folder="craft_id_artworks"
        )
        secure_url = upload_result.get("secure_url")
        if not secure_url:
            raise HTTPException(status_code=500, detail="Cloudinary did not return a URL")
        return {"file_url": secure_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

# --- NEW: SERVE STATIC FILES AND THE ROOT HTML ---

# Mount the 'static' directory to the '/static' path
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the uploader.html file at the root path
@app.get("/")
async def read_root():
    return FileResponse('uploader.html')