from fastapi import FastAPI, UploadFile, HTTPException
import shutil
from pathlib import Path
from tsr.system import TSR
from PIL import Image
import torch # лучше все импортнуть
app = FastAPI()

#Импортируем модель один раз при старте app
model = TSR.from_pretrained(
    "stabilityai/TripoSR",
    config_name="config.yaml",
    weight_name="model.ckpt"
)

model.eval() # Режим инференсаа включаем(если не включить может начать обучаться)
# Ограничение ядер, чтобы комп не вис
torch.set_num_threads(4)



BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "images"
ALLOWED_TYPE = {"image/jpeg", "image/png", "image/webp"}

# Проверка работоспособности сервера
@app.get("/")
def health():
    return {'healt message': "server is ok"}

# Проверяем, что загружаемый файл имеет допустимый тип изображения
@app.post("/upload-image/")
async def upload_image(file: UploadFile):
    if file.content_type not in ALLOWED_TYPE:
        raise HTTPException(
            status_code=400,
            detail=f"Принимаются файлы только формата png, jpeg и webp, сейчас получен {file.content_type}")

    # Формируем путь для сохранения файла в директории images/
    save_path = UPLOAD_DIR / file.filename

    # Сохраняем файл на диск
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    print(f"Файл сохранён по пути: {save_path}")

    # создаем 3д модель 
    print("Начинаем создавать 3д модель...")
    image = Image.open(save_path)
    with torch.no_grad(): # Отключаем подсчет градиентов. При обучении надо было бы включить.
        scene_codes = model([image], device="cpu")
    mesh = model.extract_mesh(scene_codes, has_vertex_color=False, resolution=128)[0]
    mesh.export("output.obj") #TODO придумать как сохранять последовательно(без перезаписи)

    # Возвращаем имя и тип сохранённого файла
    return {
        "filename": file.filename,
        "content_type": file.content_type
    }

