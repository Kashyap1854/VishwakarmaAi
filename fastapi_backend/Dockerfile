# FastAPI backend Dockerfile
FROM python:3.12-slim

WORKDIR /app

# System deps for Pillow + faiss
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install torch CPU-only first (much smaller than default CUDA build)
RUN pip install --no-cache-dir \
    torch==2.3.0 --index-url https://download.pytorch.org/whl/cpu

# Install CLIP from OpenAI github
RUN pip install --no-cache-dir \
    git+https://github.com/openai/CLIP.git

# Install faiss CPU
RUN pip install --no-cache-dir faiss-cpu==1.8.0

# Install remaining app requirements
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
