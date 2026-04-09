from fastapi import FastAPI, UploadFile, HTTPException
import shutil
from pathlib import Path
app = FastAPI()

BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "images"
ALLOWED_TYPE = {"image/jpeg", "image/png", "image/webp"}

@app.get("/")
def health():
    return {'healt message': "server is ok"}

@app.post("/upload-image/")
async def upload_image(file: UploadFile):

    if file.content_type not in ALLOWED_TYPE:
        raise HTTPException(
            status_code=400,
            detail=f"Принимаются файлы только формата png, jpeg и webp, сейчас получен {file.content_type}")

    save_path = UPLOAD_DIR / file.filename

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": file.filename,
        "content_type": file.content_type
    }

