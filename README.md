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
