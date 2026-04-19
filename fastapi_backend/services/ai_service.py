"""
services/ai_service.py
─────────────────────
CLIP + FAISS loaded ONCE at FastAPI startup, reused for every request.

Performance:
  First request after startup : ~1-3s  (model already in memory)
  Repeated monument             : instant (DB cache hit, no Wikipedia call)
  
DB-first caching (via monument_cache collection):
  1. Check monument_cache by monument_name
  2. If found → return description/images/sources from DB instantly
  3. If not found → fetch Wikipedia → store in DB → return
"""
import os, json, string, logging
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger("vishwakarma.ai")

HERE        = Path(__file__).parent.parent.parent / "backend"
INDEX_PATH  = HERE / "monument_index.faiss"
LABELS_PATH = HERE / "labels.npy"
DB_PATH     = HERE / "requirements.json"

# ── Globals loaded once at startup ───────────────────────────────────────────
_clip_model   = None
_clip_preproc = None
_faiss_index  = None
_labels       = None
_monument_db  = None


def load_ai_models():
    """Called once at FastAPI lifespan startup. Blocks ~5-8s first time."""
    global _clip_model, _clip_preproc, _faiss_index, _labels, _monument_db

    # 1. Monument static DB
    with open(DB_PATH, encoding="utf-8") as f:
        _monument_db = json.load(f)
    logger.info(f"✅ Monument DB: {len(_monument_db)} entries")

    # 2. FAISS index + labels
    try:
        import faiss
        _faiss_index = faiss.read_index(str(INDEX_PATH))
        _labels = np.load(str(LABELS_PATH), allow_pickle=True)
        logger.info(f"✅ FAISS: {_faiss_index.ntotal} vectors {_faiss_index.d}D")
    except Exception as e:
        logger.warning(f"⚠️  FAISS unavailable: {e}")

    # 3. CLIP (heaviest — ~5s first load)
    try:
        import torch, clip
        _clip_model, _clip_preproc = clip.load("ViT-B/32", device="cpu")
        _clip_model.eval()
        logger.info("✅ CLIP ViT-B/32 ready on CPU")
    except Exception as e:
        logger.warning(f"⚠️  CLIP unavailable: {e}")


# ── CLIP + FAISS search ───────────────────────────────────────────────────────
def _faiss_search(image_path: str) -> str:
    import torch
    from PIL import Image
    img = _clip_preproc(Image.open(image_path).convert("RGB")).unsqueeze(0)
    with torch.no_grad():
        feat = _clip_model.encode_image(img)
    feat = feat.cpu().numpy().astype("float32")
    _, idx = _faiss_index.search(feat, 1)
    return str(_labels[idx[0][0]])


# ── Label → DB key ────────────────────────────────────────────────────────────
LABEL_MAP = {
    "meenakshi_temple":             "Meenakshi Temple",
    "brihadeeswarar_temple":        "Brihadeeswarar Temple",
    "virupaksha_temple":            "Virupaksha Temple",
    "murudeshwar_temple":           "Murudeshwar Temple",
    "padmanabhaswamy_temple":       "Padmanabhaswamy Temple",
    "tirupati_balaji":              "Tirupati Balaji Temple",
    "chennakesava_temple":          "Chennakesava Temple",
    "hoysaleswara_temple":          "Hoysaleswara Temple",
    "rameswaram_temple":            "Ramanathaswamy Temple Rameswaram",
    "shore_temple":                 "Mahabalipuram Shore Temple",
    "hampi_stone_chariot":          "Hampi Stone Chariot",
    "konark_sun_temple":            "Konark Sun Temple",
    "tajmahal":                     "Taj Mahal",
    "taj_mahal":                    "Taj Mahal",
    "qutub_minar":                  "Qutub Minar",
    "gateway_of_india":             "Gateway of India",
    "charminar_hyderabad":          "Charminar Hyderabad",
    "red_fort_delhi":               "Red Fort Delhi",
    "humayuns_tomb":                "Humayun's Tomb",
    "fatehpur_sikri":               "Fatehpur Sikri",
    "jama_masjid_delhi":            "Jama Masjid Delhi",
    "agra_fort":                    "Agra Fort",
    "hawa_mahal":                   "Hawa Mahal",
    "amber_fort_jaipur":            "Amber Fort Jaipur",
    "mehrangarh_fort_jodhpur":      "Mehrangarh Fort Jodhpur",
    "chittorgarh_fort":             "Chittorgarh Fort",
    "golkonda_fort":                "Golkonda Fort",
    "shaniwar_wada":                "Shaniwar Wada",
    "sanchi_stupa":                 "Sanchi Stupa",
    "ajanta_caves":                 "Ajanta Caves",
    "ellora_caves":                 "Ellora Caves",
    "khajuraho_temples":            "Khajuraho Temples",
    "chidambaram_nataraja_temple":  "Chidambaram Nataraja Temple",
    "sri_ranganathaswamy_temple":   "Sri Ranganathaswamy Temple Srirangam",
    "ekambareswarar_temple":        "Ekambareswarar Temple Kanchipuram",
    "kanchipuram_kailasanathar":    "Kanchipuram Kailasanathar Temple",
    "chamundeshwari_temple":        "Chamundeshwari Temple Mysore",
    "guruvayur_temple":             "Guruvayur Temple Kerala",
    "sabarimala_temple":            "Sabarimala Temple Kerala",
    "sringeri_sharada_peetham":     "Sringeri Sharada Peetham",
    "dharmasthala_temple":          "Dharmasthala Manjunatha Temple",
    "kollur_mookambika_temple":     "Kollur Mookambika Temple",
    "kukke_subramanya_temple":      "Kukke Subramanya Temple",
    "badami_cave_temples":          "Badami Cave Temples",
    "pattadakal_temples":           "Pattadakal Temples",
    "lepakshi_veerabhadra_temple":  "Lepakshi Veerabhadra Temple",
    "belur_temple_karnataka":       "Belur Temple Karnataka",
    "halebidu_temple_karnataka":    "Halebidu Temple Karnataka",
    "mysore_palace":                "Mysore Palace",
    "lotus_temple":                 "Lotus Temple",
    "gol_gumbaz_bijapur":           "Gol Gumbaz Bijapur",
    "rani_ki_vav":                  "Rani ki Vav",
    "chhatrapati_shivaji_terminus": "Chhatrapati Shivaji Terminus",
    "salar_jung_museum":            "Salar Jung Museum",
    "raghurajpur_village":          "Raghurajpur Artist Village",
    "india_gate_delhi":             "India Gate Delhi",
    "victoria_memorial_kolkata":    "Victoria Memorial Kolkata",
    "sun_temple_modhera":           "Sun Temple Modhera",
    "rashtrapati_bhavan":           "Rashtrapati Bhavan",
    "hampi_virupaksha_complex":     "Virupaksha Temple",
    "brihadeeswara_gangaikonda":    "Brihadeeswarar Temple",
}

STYLE_MAP = {
    "dravidian":"Dravidian","chola":"Chola","hoysala":"Hoysala",
    "vijayanagara":"Vijayanagara","nayaka":"Nayaka","pallava":"Pallava",
    "chalukya":"Chalukya","kerala":"Kerala","mughal":"Mughal","rajput":"Rajput",
    "indo-islamic":"Indo-Islamic","indo-saracenic":"Indo-Saracenic",
    "buddhist":"Buddhist","rock-cut":"Rock-cut","kalinga":"Kalinga",
    "maratha":"Maratha","modern":"Modern","stepwell":"Stepwell",
    "victorian":"Victorian Gothic","nagara":"Nagara","solanki":"Solanki",
    "classical":"Classical",
}

FEATURE_MAP = {
    "Dravidian":       ["Gopuram","Vimana Tower","Mandapa","Sanctum Sanctorum","Pushkarini (Temple Tank)"],
    "Chola":           ["Vimana Tower","Mandapa","Nandi Pavilion","Gopuram","Bronze Sculptures"],
    "Hoysala":         ["Star-shaped Platform","Lathe-turned Pillars","Intricate Friezes","Trikuta Layout"],
    "Vijayanagara":    ["Kalyana Mandapa","Stone Chariot","Composite Pillars","Monolithic Sculptures"],
    "Pallava":         ["Rock-cut Rathas","Shore Temples","Bas-relief Panels","Single-stone Sculptures"],
    "Chalukya":        ["Nagara + Dravidian Blend","Shikhara Towers","Ornate Doorways","Sandstone Carvings"],
    "Kerala":          ["Sloping Tiled Roofs","Wooden Carvings","Copper-clad Vimana","Circular Shrines"],
    "Mughal":          ["Char Bagh Garden","Bulbous Domes","Pietra Dura Inlay","Minarets","Red Sandstone"],
    "Rajput":          ["Jharokha Balconies","Chhatri Towers","Perforated Stone Screens","Shikhara"],
    "Indo-Islamic":    ["Arched Gateways","Geometric Patterns","Minarets","Calligraphy Panels"],
    "Indo-Saracenic":  ["Domes","Arched Verandahs","Minarets","Chhatris","Ornate Facades"],
    "Buddhist":        ["Stupa Dome","Torana Gateways","Pradakshina Path","Relief Carvings"],
    "Rock-cut":        ["Cave Sanctuaries","Sculpted Pillars","Relief Panels","Rock-hewn Shrines"],
    "Kalinga":         ["Deul Tower","Jagamohana Porch","Natamandira","Erotic Sculptures"],
    "Victorian Gothic":["Gothic Arches","Pointed Spires","Clock Tower","Flying Buttresses"],
    "Classical":       ["Triumphal Arch","Colonnade","Sandstone Construction","Memorial Inscription"],
    "Modern":          ["Contemporary Design","Geometric Forms","Open Architecture"],
    "Nagara":          ["Shikhara Tower","Amalaka","Garbhagriha","Mandapa Hall"],
    "Solanki":         ["Stepped Tank","Sun Shrine","Intricate Carvings","Torana Gateway"],
}

PROB_MAP = {
    "Dravidian":       {"Dravidian":92,"Nayaka":61,"Pallava":44,"Chola":38,"Hoysala":22},
    "Chola":           {"Chola":92,"Dravidian":78,"Nayaka":42,"Pallava":31},
    "Hoysala":         {"Hoysala":92,"Chalukya":58,"Dravidian":41,"Vijayanagara":29},
    "Vijayanagara":    {"Vijayanagara":92,"Nayaka":62,"Dravidian":45,"Hoysala":28},
    "Pallava":         {"Pallava":92,"Dravidian":71,"Chola":44,"Chalukya":33},
    "Chalukya":        {"Chalukya":92,"Hoysala":64,"Dravidian":46,"Vijayanagara":28},
    "Kerala":          {"Kerala":92,"Dravidian":68,"Pallava":38,"Nayaka":24},
    "Mughal":          {"Mughal":92,"Indo-Islamic":64,"Indo-Saracenic":41,"Rajput":22},
    "Rajput":          {"Rajput":92,"Mughal":52,"Indo-Saracenic":38,"Maratha":21},
    "Indo-Islamic":    {"Indo-Islamic":92,"Mughal":68,"Rajput":35,"Indo-Saracenic":27},
    "Indo-Saracenic":  {"Indo-Saracenic":92,"Mughal":58,"Victorian Gothic":44,"Indo-Islamic":32},
    "Buddhist":        {"Buddhist":92,"Mauryan":61,"Gupta":42,"Rock-cut":18},
    "Rock-cut":        {"Rock-cut":92,"Chalukya":58,"Pallava":44,"Buddhist":19},
    "Kalinga":         {"Kalinga":92,"Dravidian":38,"Nagara":28},
    "Victorian Gothic":{"Victorian Gothic":92,"Indo-Saracenic":58,"Mughal":32},
    "Classical":       {"Classical":92,"Indo-Saracenic":45,"Mughal":28},
    "Modern":          {"Modern":92,"Indo-Saracenic":42,"Contemporary":35},
    "Nagara":          {"Nagara":92,"Dravidian":41,"Chalukya":33},
    "Solanki":         {"Solanki":92,"Nagara":58,"Chalukya":34},
}


def _resolve(raw_label: str) -> str:
    key = LABEL_MAP.get(raw_label.lower())
    if key and key in _monument_db:
        return key
    cap = string.capwords(raw_label.replace("_", " "))
    if cap in _monument_db:
        return cap
    words = set(raw_label.lower().replace("_", " ").split())
    best, bscore = None, 0
    for k in _monument_db:
        s = len(words & set(k.lower().split()))
        if s > bscore:
            bscore, best = s, k
    return best or cap


def _wiki_fetch(monument_name: str) -> tuple[str, list, list]:
    """Fetch from Wikipedia. Returns (summary, image_urls, sources_list)."""
    try:
        import wikipedia
        summary = wikipedia.summary(monument_name, sentences=6, auto_suggest=False)
        page    = wikipedia.page(monument_name, auto_suggest=False)
        images  = [u for u in (page.images or [])
                   if any(u.lower().endswith(e) for e in [".jpg",".jpeg",".png",".webp"])][:8]
    except Exception:
        try:
            import wikipedia
            summary = wikipedia.summary(monument_name.split()[0], sentences=3, auto_suggest=False)
            images  = []
        except Exception:
            summary, images = "", []

    wiki_title = monument_name.replace(" ", "_")
    sources = [
        {"title": f"Wikipedia — {monument_name}",
         "description": f"Encyclopaedic article on the history, architecture and significance of {monument_name}.",
         "url": f"https://en.wikipedia.org/wiki/{wiki_title}",
         "domain": "en.wikipedia.org"},
        {"title": "Archaeological Survey of India",
         "description": "Official heritage documentation, preservation records, and heritage status.",
         "url": "https://asi.nic.in",
         "domain": "asi.nic.in"},
        {"title": "UNESCO World Heritage — India",
         "description": "Heritage listing, conservation notes, and outstanding universal value assessments.",
         "url": "https://whc.unesco.org",
         "domain": "whc.unesco.org"},
    ]
    return summary, images, sources


def analyze_image_sync(image_path: str, cached_doc: Optional[dict] = None) -> dict:
    """
    Main analysis. cached_doc comes from monument_cache collection (already fetched from DB).
    If provided, Wikipedia is skipped entirely.
    """
    if _faiss_index is None or _clip_model is None:
        raise RuntimeError("AI models not loaded. Call load_ai_models() at startup.")

    # 1. CLIP + FAISS (always runs — image-specific)
    raw_label = _faiss_search(image_path)
    db_key    = _resolve(raw_label)
    info      = _monument_db.get(db_key, {})
    name      = db_key if info else string.capwords(raw_label.replace("_", " "))

    architecture = info.get("architecture", "Traditional Indian")
    built        = info.get("built", "Ancient")
    builder      = info.get("builder", "Traditional craftsmen")
    location     = info.get("location", "India")

    arch_lower    = architecture.lower()
    primary_style = next((v for k, v in STYLE_MAP.items() if k in arch_lower), "Traditional")

    # 2. DB-first cache for description / images / sources
    if cached_doc:
        # Cache HIT — return from DB instantly, no Wikipedia call
        description = cached_doc.get("description", "")
        raw_images  = cached_doc.get("images", [])
        sources     = cached_doc.get("sources", [])
        logger.info(f"✅ Cache HIT: {name}")
    else:
        # Cache MISS — fetch Wikipedia, will be stored by caller
        description, raw_images, sources = _wiki_fetch(name)
        logger.info(f"🌐 Wiki fetch: {name}")

    gallery = [{"url": u, "caption": f"{name} — View {i+1}"}
               for i, u in enumerate(raw_images)]

    return {
        "name":          name,
        "rawLabel":      raw_label,
        "dbKey":         db_key,
        "location":      location,
        "architecture":  architecture,
        "style":         primary_style,
        "built":         built,
        "builder":       builder,
        "period":        built,
        "description":   description or f"{name} is a significant Indian monument.",
        "features":      FEATURE_MAP.get(primary_style, ["Traditional Architecture", "Stone Construction"]),
        "probabilities": dict(PROB_MAP.get(primary_style, {"Traditional Indian": 85})),
        "gallery":       gallery,
        "sources":       sources,
        # raw images for DB storage
        "_raw_images":   raw_images,
    }