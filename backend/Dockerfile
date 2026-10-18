FROM python:3.11-slim

# System dependencies for OpenCV, FFmpeg, and audio decoding
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY backend/ ./backend/
COPY ml/ ./ml/
COPY alembic.ini ./

# Install python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    pydantic-settings \
    sqlalchemy \
    alembic \
    psycopg2-binary \
    redis \
    celery \
    python-multipart \
    puremagic \
    imageio \
    imageio-ffmpeg \
    torch \
    torchvision \
    timm \
    opencv-python-headless \
    pillow \
    librosa \
    soundfile \
    scipy \
    numpy \
    scikit-learn

# Create storage directory
RUN mkdir -p storage/uploads storage/thumbnails storage/processed

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
