# 2D → 3D Converter

Convert images into 3D models using [TripoSR](https://github.com/VAST-AI-Research/TripoSR) — a fast single-image 3D reconstruction model by Stability AI.

Upload a photo, adjust settings, and download a `.obj` file ready for use in Blender, Unity, or any 3D editor.

---

## Quick Start

> Requires [Docker](https://www.docker.com/get-started/) installed on your machine.

```bash
git clone https://github.com/qwert-3001/2D-to-3D-app.git
cd fast_api_2d_to_3d_project
docker compose up --build
```

Then open **[http://localhost:8000](http://localhost:8000)** in your browser.

> First launch takes longer — the model (~1 GB) downloads from HuggingFace automatically and is cached for future runs.

---

## Usage

1. **Upload** an image (PNG, JPEG, or WebP)
2. **Select** resolution — higher resolution = more detail, but slower and more memory-intensive
3. **Click** "Создать 3D модель"
4. **Download** the generated `.obj` file

### Resolution guide

| Resolution | Speed     | RAM usage  | Recommended for        |
|------------|-----------|------------|------------------------|
| 128        | Fast      | ~2 GB      | Quick previews         |
| 256        | Slow      | ~6 GB      | Better quality         |
| 512+       | Very slow | ~11+ GB    | High-end machines only |

---

## API

The server exposes a REST API. Interactive docs available at [http://localhost:8000/docs](http://localhost:8000/docs).

| Method | Endpoint              | Description                         |
|--------|-----------------------|-------------------------------------|
| `POST` | `/upload-image/`      | Upload an image, returns `image_id` |
| `POST` | `/generate-3d/`       | Generate `.obj` from `image_id`     |
| `GET`  | `/images/`            | List all uploaded images            |
| `GET`  | `/images/{filename}`  | Get a specific image                |

---

## Stack

- **FastAPI** — web framework
- **TripoSR** — 3D reconstruction model
- **PyTorch** — ML inference (CPU)
- **Docker** — containerization
- **uv** — Python package manager

---

## Project Structure

```
├── app/
│   ├── main.py          # FastAPI application
│   └── tsr/             # TripoSR model code
├── static/
│   └── index.html       # Frontend
├── Dockerfile
├── docker-compose.yaml
└── pyproject.toml
```

---

## Local Development (without Docker)

Requires: Python 3.12, [uv](https://github.com/astral-sh/uv), cmake, g++

```bash
uv sync
make run app
```
