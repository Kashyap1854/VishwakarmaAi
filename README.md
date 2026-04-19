# Vishwakarma AI 🏛️

AI-powered recognition and analysis of Indian monument architecture.
Uses CLIP + FAISS for image search, Wikipedia for descriptions, Ollama/Mistral for LLM enrichment.

---

## Project Structure

```
vishwakarma_clean/
├── backend/
│   ├── server.js             ← Express API server (port 5000)
│   ├── analyze.py            ← Python: CLIP search → Wikipedia → LLM → JSON
│   ├── search.py             ← CLIP + FAISS visual search
│   ├── extract_features.py   ← Build FAISS index from dataset images
│   ├── build_dataset.py      ← Download training images via Bing
│   ├── llm_extractor.py      ← Ollama/Mistral structured extraction
│   ├── requirements.json     ← 40+ monument static database
│   ├── requirements.txt      ← Python deps list
│   ├── install.bat           ← Windows one-click installer
│   ├── install.sh            ← Mac/Linux one-click installer
│   └── package.json
│
├── frontend/
│   ├── src/App.jsx           ← Full React UI (same design, API-connected)
│   ├── src/main.jsx
│   ├── vite.config.js        ← Dev proxy → backend:5000
│   ├── index.html
│   └── package.json
│
└── README.md
```

---

## ⚡ Quick Setup (Windows)

### Step 1 — Install Python dependencies
```
cd backend
install.bat
```
Or manually, one by one:
```
pip install icrawler
pip install Pillow numpy wikipedia ollama
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install git+https://github.com/openai/CLIP.git
pip install faiss-cpu
```

### Step 2 — Build the AI index (one-time setup)
```
python build_dataset.py
python extract_features.py
```
This downloads ~900 temple images and builds the FAISS search index.
Takes 5–15 minutes depending on internet speed.

### Step 3 — Install Node dependencies
```
npm install         (in backend/)
cd ../frontend
npm install
```

### Step 4 — (Optional) Start Ollama for LLM enrichment
Download from https://ollama.com, then:
```
ollama pull mistral
ollama serve
```
> If Ollama is not running, the app still works — it falls back to the static database.

### Step 5 — Run the app
**Terminal 1 (backend):**
```
cd backend
npm start
```
**Terminal 2 (frontend):**
```
cd frontend
npm run dev
```

Open: http://localhost:3000

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/analyze` | Upload image → JSON analysis |
| GET  | `/api/monuments` | Returns monument database |
| GET  | `/api/health` | Health check |

### Response example
```json
{
  "name": "Brihadeeswarar Temple",
  "location": "Thanjavur, Tamil Nadu",
  "architecture": "Dravidian (Chola)",
  "style": "Chola",
  "built": "1003-1010",
  "builder": "Rajaraja Chola I",
  "confidence": 0.94,
  "description": "The Brihadeeswarar Temple...",
  "features": ["Vimana Tower", "Mandapa", "Nandi Pavilion"],
  "probabilities": { "Dravidian": 94, "Chola": 88, "Hoysala": 32 },
  "sources": [{ "title": "...", "url": "...", "domain": "..." }]
}
```

---

## 🐳 Docker Setup (Recommended)

### 1. Build and Run All Services

This will start the backend (FastAPI), frontend (React), and MongoDB database using Docker Compose.

```sh
docker-compose up --build
```
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- MongoDB: localhost:27017

### 2. Stopping Services

```sh
docker-compose down
```

### 3. Rebuilding Only a Specific Service

```sh
docker-compose build --no-cache backend
```

---

## 🖥️ Manual (Non-Docker) Setup

Follow the steps in **Quick Setup (Windows)** or adapt for your OS. You can run backend, frontend, and database manually if you prefer not to use Docker.

---

## ⚡ One-Command Quick Start (Docker)

If you have Docker and Docker Compose installed, just run:

```sh
docker-compose up --build
```

---

## 🔑 Environment Variables

Some services require environment variables for configuration. You can set these in a `.env` file in the relevant directory or use the provided defaults in `docker-compose.yml`.

### Example `.env` for FastAPI Backend (`fastapi_backend/.env`):
```
MONGO_URI=mongodb://mongo:27017/vishwakarma_ai
MONGO_DB=vishwakarma_ai
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
PYTHON_PATH=python3
```
- If you use Docker Compose, these are set automatically.
- For manual runs, copy the above into `fastapi_backend/.env` and adjust as needed.

> **Note:** Never commit `.env` files with secrets or credentials to Git. They are already included in `.gitignore`.

---
