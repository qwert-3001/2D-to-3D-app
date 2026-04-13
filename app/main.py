import os
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
import uuid
import logging # Для логов, вместо print
import shutil
from pathlib import Path
from tsr.system import TSR
from PIL import Image
import torch # лучше все импортнуть

app = FastAPI()

#Фронт
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")

#Настраиваем логи
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) #Логер для текущего модуля, понять откуда идет лог

#Импортируем модель один раз при старте app
model = TSR.from_pretrained(
    "stabilityai/TripoSR",
    config_name="config.yaml",
    weight_name="model.ckpt"
)

model.eval() # Режим инференсаа включаем(если не включить может начать обучаться)

# Ограничение ядер, чтобы комп не вис
# Узнаем сколько на процессоре ядер и будем ограничивать
cpu_count = os.cpu_count()
torch.set_num_threads(max(1, cpu_count // 2)) # Если ядро одно, то оставляем 1



BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "images"
ALLOWED_TYPE = {"image/jpeg", "image/png", "image/webp"}

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Главная страница
@app.get("/")
def index():
    return FileResponse("static/index.html")

@app.post("/upload-image/")
async def upload_image(file: UploadFile):

    # check file format
    if file.content_type not in ALLOWED_TYPE:
        raise HTTPException(
            status_code=400,
            detail=f"Принимаются файлы только формата png, jpeg и webp, сейчас получен {file.content_type}"
        )
    
    # Формируем путь для сохранения файла в директории images/
    original_filename = Path(file.filename)
    save_path = UPLOAD_DIR / (original_filename.stem + f"_{uuid.uuid4()}" + original_filename.suffix)

    # Сохраняем файл на диск
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.info(f"Файл сохранён по пути: {save_path}")

    return {"image_id": save_path.name} 

# генерация 3д модели по файлу
@app.post("/generate-3d/")
async def generate_3d(image_id: str, resolution: int = 128, vertex_color: bool = False):

    save_path = UPLOAD_DIR / image_id

    # создаем 3д модель
    logger.info("Начинаем создавать 3д модель...")
    image = Image.open(save_path)
    with torch.no_grad(): # Отключаем подсчет градиентов. При обучении надо было бы включить.
        scene_codes = model([image], device="cpu")
    mesh = model.extract_mesh(scene_codes, has_vertex_color=vertex_color, resolution=resolution)[0]

    output_path = OUTPUT_DIR / (Path(image_id).stem + ".obj")

    mesh.export(str(output_path))

    logger.info(f"3д модель сохранена по пути: {output_path}")

    return FileResponse(
        output_path,
        filename=Path(image_id).stem + ".obj")

# Получение списка всех загруженных изображений
@app.get("/images/")
def all_image():
    logger.info("Получаем список всех изображений")
    return [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]

@app.get("/images/{filename}")
def get_image(filename: str):
    image_path = UPLOAD_DIR / filename
    logger.info(f"Получаем изображение по пути {image_path}")
    return FileResponse(image_path)