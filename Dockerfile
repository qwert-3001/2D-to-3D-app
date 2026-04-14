FROM python:3.12-slim

#Устнановка зависимостей и чистка кэша
RUN apt-get update && apt-get install -y cmake git g++ && rm -rf /var/lib/apt/lists/*

RUN pip install uv

WORKDIR /project

COPY pyproject.toml uv.lock ./

RUN uv venv
RUN uv pip install "pybind11[global]" scikit-build-core
RUN uv sync --frozen

COPY app/ ./app/
COPY static/ ./static/

RUN mkdir -p images output

ENV PYTHONPATH=app
ENV PYTHONUNBUFFERED=1

CMD ["uv", "run", "fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
