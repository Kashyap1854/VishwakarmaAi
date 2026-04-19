# Vishwakarma AI — FastAPI Backend

Complete REST API with MongoDB storage via Motor (async).

## Structure

```
fastapi_backend/
├── main.py                  ← FastAPI app entry point
├── config.py                ← Settings from .env
├── database.py              ← Motor client + collection helpers
├── models.py                ← All Pydantic schemas
├── auth.py                  ← JWT + password hashing
├── seed.py                  ← One-time monument DB seeder
├── .env                     ← Environment variables (edit this)
├── requirements.txt         ← Python dependencies
├── uploads/                 ← Temp upload folder (auto-created)
└── routers/
    ├── auth_router.py       ← /api/auth/*
    ├── analyze_router.py    ← /api/analyze
    ├── history_router.py    ← /api/history/*
    └── monuments_router.py  ← /api/monuments/*
```

## API Endpoints

### Auth
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | No | Register new user |
| POST | `/api/auth/login` | No | Login, get JWT |
| GET | `/api/auth/me` | Yes | Get current user |
| DELETE | `/api/auth/account` | Yes | Delete account |

### Analysis
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/analyze` | Yes | Upload image → AI analysis → stored in MongoDB |

### History
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/history` | Yes | Paginated list (`?skip=0&limit=20`) |
| GET | `/api/history/{id}` | Yes | Full single analysis |
| DELETE | `/api/history/{id}` | Yes | Delete one analysis |
| DELETE | `/api/history` | Yes | Clear all analyses for user |

### Monuments
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/monuments` | No | List all (`?style=&search=`) |
| GET | `/api/monuments/{name}` | No | Single monument |
| POST | `/api/monuments/seed` | No | Force re-seed from requirements.json |

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Server + MongoDB status |

## MongoDB Collections

| Collection | Description |
|------------|-------------|
| `users` | Registered user accounts (hashed passwords) |
| `analyses` | Every completed AI analysis — full data stored |
| `monuments` | Static monument database (seeded from requirements.json) |

## Setup & Run

### 1. Edit .env
```
MONGO_URI=mongodb://localhost:27017      # or Atlas URI
MONGO_DB=vishwakarma_ai
SECRET_KEY=your_long_random_secret_here
```

### 2. Install dependencies
```
pip install -r requirements.txt
pip install pydantic-settings
```

### 3. Start server
```
uvicorn main:app --reload --port 5000
```

### 4. View interactive docs
Open: http://localhost:5000/docs

## Data stored per analysis in MongoDB

Every field from the AI pipeline is stored:
- User email + image filename + size + mimetype
- Monument name, raw FAISS label, DB key
- Location, architecture style, built year, builder, period
- Full Wikipedia description
- Features list
- Style probability distribution (dict)
- Gallery images (url + caption)
- Research sources (title, description, url, domain)
- Created timestamp (UTC)
