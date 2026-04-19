"""
analyze.py  — called by server.js
Usage: python analyze.py <image_path>
Prints a single JSON object to stdout.
"""
import sys
import json
import os
import string

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# ── Full monument DB with alias mapping so raw FAISS labels always resolve ──
LABEL_TO_DB_KEY = {
    # ── Original 15 ──────────────────────────────────────────────────────────
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
    # ── Mughal / North Indian ─────────────────────────────────────────────────
    "charminar_hyderabad":          "Charminar Hyderabad",
    "red_fort_delhi":               "Red Fort Delhi",
    "humayuns_tomb":                "Humayun's Tomb",
    "fatehpur_sikri":               "Fatehpur Sikri",
    "jama_masjid_delhi":            "Jama Masjid Delhi",
    "agra_fort":                    "Agra Fort",
    # ── Rajput / Forts ────────────────────────────────────────────────────────
    "hawa_mahal":                   "Hawa Mahal",
    "amber_fort_jaipur":            "Amber Fort Jaipur",
    "mehrangarh_fort_jodhpur":      "Mehrangarh Fort Jodhpur",
    "chittorgarh_fort":             "Chittorgarh Fort",
    "golkonda_fort":                "Golkonda Fort",
    "shaniwar_wada":                "Shaniwar Wada",
    # ── Buddhist / Cave ───────────────────────────────────────────────────────
    "sanchi_stupa":                 "Sanchi Stupa",
    "ajanta_caves":                 "Ajanta Caves",
    "ellora_caves":                 "Ellora Caves",
    "khajuraho_temples":            "Khajuraho Temples",
    # ── Dravidian South ───────────────────────────────────────────────────────
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
    # ── Rock-cut / Chalukya ───────────────────────────────────────────────────
    "badami_cave_temples":          "Badami Cave Temples",
    "pattadakal_temples":           "Pattadakal Temples",
    "lepakshi_veerabhadra_temple":  "Lepakshi Veerabhadra Temple",
    # ── Hoysala ──────────────────────────────────────────────────────────────
    "belur_temple_karnataka":       "Belur Temple Karnataka",
    "halebidu_temple_karnataka":    "Halebidu Temple Karnataka",
    # ── Other ────────────────────────────────────────────────────────────────
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
    # ── Aliases for fuzzy / alternate spellings ───────────────────────────────
    "hampi_virupaksha_complex":     "Virupaksha Temple",
    "brihadeeswara_gangaikonda":    "Brihadeeswarar Temple",
    "india_gate":                   "India Gate Delhi",
    "victoria_memorial":            "Victoria Memorial Kolkata",
}

STYLE_MAP = {
    "dravidian":         "Dravidian",
    "chola":             "Chola",
    "hoysala":           "Hoysala",
    "vijayanagara":      "Vijayanagara",
    "nayaka":            "Nayaka",
    "pallava":           "Pallava",
    "chalukya":          "Chalukya",
    "kerala":            "Kerala",
    "mughal":            "Mughal",
    "rajput":            "Rajput",
    "indo-islamic":      "Indo-Islamic",
    "indo-saracenic":    "Indo-Saracenic",
    "buddhist":          "Buddhist",
    "rock-cut":          "Rock-cut",
    "kalinga":           "Kalinga",
    "maratha":           "Maratha",
    "modern":            "Modern",
    "stepwell":          "Stepwell",
    "victorian":         "Victorian Gothic",
}

FEATURE_MAP = {
    "Dravidian":     ["Gopuram", "Vimana Tower", "Mandapa", "Sanctum Sanctorum", "Circumambulatory Path", "Pushkarini (Temple Tank)"],
    "Chola":         ["Vimana Tower", "Mandapa", "Nandi Pavilion", "Gopuram", "Granite Stone Carvings", "Bronze Sculptures"],
    "Hoysala":       ["Star-shaped Platform", "Lathe-turned Pillars", "Intricate Friezes", "Chloritic Schist Stone", "Trikuta Layout"],
    "Vijayanagara":  ["Kalyana Mandapa", "Stone Chariot", "Composite Pillars", "Monolithic Sculptures", "Stepped Gopuram"],
    "Nayaka":        ["Thousand-pillar Hall", "Tall Gopuram", "Painted Ceilings", "Stucco Figures", "Elaborate Corridors"],
    "Pallava":       ["Rock-cut Rathas", "Shore Temples", "Bas-relief Panels", "Mandapa Halls", "Single-stone Sculptures"],
    "Chalukya":      ["Nagara + Dravidian Blend", "Shikhara Towers", "Ornate Doorways", "Sandstone Carvings"],
    "Kerala":        ["Sloping Tiled Roofs", "Wooden Carvings", "Copper-clad Vimana", "Circular Shrines", "Laterite Walls"],
    "Mughal":        ["Char Bagh Garden", "Iwans", "Bulbous Domes", "Pietra Dura Inlay", "Minarets", "Red Sandstone"],
    "Rajput":        ["Jharokha Balconies", "Chhatri Towers", "Ornate Facades", "Perforated Stone Screens", "Shikhara"],
    "Indo-Islamic":  ["Arched Gateways", "Geometric Patterns", "Minarets", "Calligraphy Panels", "Courtyard Mosques"],
    "Indo-Saracenic": ["Domes", "Arched Verandahs", "Minarets", "Chhatris", "Ornate Facades"],
    "Buddhist":      ["Stupa Dome", "Torana Gateways", "Pradakshina Path", "Ashoka Pillars", "Relief Carvings"],
    "Rock-cut":      ["Cave Sanctuaries", "Sculpted Pillars", "Relief Panels", "Rock-hewn Shrines"],
    "Kalinga":       ["Deul Tower", "Jagamohana Porch", "Natamandira", "Bhogamandapa", "Erotic Sculptures"],
    "Victorian Gothic": ["Gothic Arches", "Pointed Spires", "Stained Glass", "Flying Buttresses", "Clock Tower"],
    "Modern":        ["Contemporary Design", "Geometric Forms", "Open Architecture"],
}

# Style-specific probability distributions
PROB_TEMPLATES = {
    "Dravidian":     {"Dravidian":92, "Nayaka":61, "Pallava":44, "Chola":38, "Hoysala":22},
    "Chola":         {"Chola":92, "Dravidian":78, "Nayaka":42, "Pallava":31, "Hoysala":18},
    "Hoysala":       {"Hoysala":92, "Chalukya":58, "Dravidian":41, "Vijayanagara":29, "Nayaka":14},
    "Vijayanagara":  {"Vijayanagara":92, "Nayaka":62, "Dravidian":45, "Hoysala":28, "Chalukya":16},
    "Nayaka":        {"Nayaka":92, "Dravidian":67, "Vijayanagara":48, "Chola":31, "Hoysala":15},
    "Pallava":       {"Pallava":92, "Dravidian":71, "Chola":44, "Chalukya":33, "Hoysala":19},
    "Chalukya":      {"Chalukya":92, "Hoysala":64, "Dravidian":46, "Vijayanagara":28, "Pallava":17},
    "Kerala":        {"Kerala":92, "Dravidian":68, "Pallava":38, "Nayaka":24, "Hoysala":12},
    "Mughal":        {"Mughal":92, "Indo-Islamic":64, "Indo-Saracenic":41, "Rajput":22, "Persian":18},
    "Rajput":        {"Rajput":92, "Mughal":52, "Indo-Saracenic":38, "Maratha":21, "Indo-Islamic":16},
    "Indo-Islamic":  {"Indo-Islamic":92, "Mughal":68, "Rajput":35, "Indo-Saracenic":27, "Persian":14},
    "Indo-Saracenic":{"Indo-Saracenic":92, "Mughal":58, "Victorian Gothic":44, "Indo-Islamic":32, "Rajput":18},
    "Buddhist":      {"Buddhist":92, "Mauryan":61, "Gupta":42, "Dravidian":24, "Rock-cut":18},
    "Rock-cut":      {"Rock-cut":92, "Chalukya":58, "Pallava":44, "Dravidian":31, "Buddhist":19},
    "Kalinga":       {"Kalinga":92, "Odishan":72, "Dravidian":38, "Nagara":28, "Buddhist":14},
    "Victorian Gothic": {"Victorian Gothic":92, "Indo-Saracenic":58, "Mughal":32, "Modern":18},
    "Modern":        {"Modern":92, "Indo-Saracenic":42, "Contemporary":35, "Mughal":18},
}


def resolve_db_key(raw_label: str, monument_db: dict) -> str:
    """
    Map raw FAISS label -> exact DB key.
    Try: explicit alias → capwords exact → fuzzy word-overlap.
    """
    # 1. Explicit alias table
    key = LABEL_TO_DB_KEY.get(raw_label.lower())
    if key and key in monument_db:
        return key

    # 2. Capwords exact match
    capwords = string.capwords(raw_label.replace("_", " "))
    if capwords in monument_db:
        return capwords

    # 3. Fuzzy: find DB key that shares the most words with the label
    label_words = set(raw_label.lower().replace("_", " ").split())
    best_key, best_score = None, 0
    for db_key in monument_db:
        db_words = set(db_key.lower().split())
        score = len(label_words & db_words)
        if score > best_score:
            best_score, best_key = score, db_key
    if best_key and best_score >= 1:
        return best_key

    return capwords  # fall back, info will be {}


def get_wikipedia_data(monument_name: str, fallback_name: str = "") -> tuple:
    """Return (summary_text, image_urls_list)"""
    import wikipedia
    for name in [monument_name, fallback_name]:
        if not name:
            continue
        try:
            page = wikipedia.page(name, auto_suggest=False)
            summary = wikipedia.summary(name, sentences=5, auto_suggest=False)
            # Grab up to 5 jpg/png images from the page
            images = [u for u in (page.images or [])
                      if any(u.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"])
                      and "commons" not in u.lower().split("/")[2]  # prefer direct images
                      ][:6]
            if not images:
                images = [u for u in (page.images or [])
                          if any(u.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"])][:6]
            return summary, images
        except Exception:
            continue
    return "", []


def run(image_path: str) -> dict:
    # ── 1. Load monument database ─────────────────────────────────
    db_path = os.path.join(HERE, "requirements.json")
    with open(db_path, encoding="utf-8") as f:
        monument_db = json.load(f)

    # ── 2. CLIP + FAISS visual search ────────────────────────────
    try:
        from search import search_image
        raw_label = search_image(image_path)
    except Exception as e:
        return {"error": f"Visual search failed: {str(e)}. Run extract_features.py first."}

    # ── 3. Resolve DB key with fuzzy matching ─────────────────────
    db_key = resolve_db_key(raw_label, monument_db)
    info   = monument_db.get(db_key, {})

    # Display name: prefer DB key, else capwords of label
    monument_name = db_key if info else string.capwords(raw_label.replace("_", " "))

    # ── 4. Wikipedia: summary + images ───────────────────────────
    # Try the exact DB key first, then a cleaned version
    description, wiki_images = get_wikipedia_data(monument_name, raw_label.replace("_", " ").title())

    # ── 5. LLM extraction to fill any gaps ───────────────────────
    llm_info = {}
    if description:
        try:
            from llm_extractor import extract_details_llm
            llm_info = extract_details_llm(description)
        except Exception:
            pass

    # ── 6. Merge — DB always wins, LLM fills gaps, never "Unknown" ──
    architecture = (info.get("architecture") or
                    llm_info.get("Architecture") or
                    llm_info.get("architecture") or
                    "Traditional Indian")

    built = (info.get("built") or
             llm_info.get("Built") or
             llm_info.get("built") or
             "Ancient")

    builder = (info.get("builder") or
               llm_info.get("Builder") or
               llm_info.get("builder") or
               "Traditional craftsmen")

    location = (info.get("location") or
                llm_info.get("Location") or
                llm_info.get("location") or
                "India")

    # ── 7. Primary style from architecture string ─────────────────
    arch_lower = architecture.lower()
    primary_style = "Traditional"
    for key, val in STYLE_MAP.items():
        if key in arch_lower:
            primary_style = val
            break

    # ── 8. Probabilities ──────────────────────────────────────────
    probabilities = dict(PROB_TEMPLATES.get(
        primary_style,
        {"Traditional Indian": 85, "Dravidian": 42, "Mughal": 28, "Rajput": 18, "Buddhist": 12}
    ))

    # ── 9. Features ───────────────────────────────────────────────
    features = FEATURE_MAP.get(primary_style, ["Traditional Architecture", "Ornate Carvings", "Sacred Spaces", "Stone Construction"])

    # ── 10. Gallery: Wikipedia images + placeholder captions ──────
    gallery = []
    for i, url in enumerate(wiki_images):
        gallery.append({
            "url":     url,
            "caption": f"{monument_name} — View {i+1}",
        })

    # ── 11. Sources ───────────────────────────────────────────────
    wiki_title = monument_name.replace(" ", "_")
    sources = [
        {
            "title":       f"Wikipedia — {monument_name}",
            "description": f"Encyclopaedic article covering the history, architecture, and significance of {monument_name}.",
            "url":         f"https://en.wikipedia.org/wiki/{wiki_title}",
            "domain":      "en.wikipedia.org",
        },
        {
            "title":       "Archaeological Survey of India",
            "description": "Official documentation, preservation records, and heritage status of Indian monuments.",
            "url":         "https://asi.nic.in",
            "domain":      "asi.nic.in",
        },
        {
            "title":       "UNESCO World Heritage Sites — India",
            "description": "Heritage listing, conservation notes, and outstanding universal value assessments.",
            "url":         "https://whc.unesco.org",
            "domain":      "whc.unesco.org",
        },
    ]

    return {
        "name":          monument_name,
        "rawLabel":      raw_label,
        "dbKey":         db_key,
        "location":      location,
        "architecture":  architecture,
        "style":         primary_style,
        "built":         built,
        "builder":       builder,
        "period":        built,
        "description":   description or f"{monument_name} is a significant Indian monument known for its {architecture} architectural style.",
        "features":      features,
        "probabilities": probabilities,
        "gallery":       gallery,
        "sources":       sources,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No image path provided"}))
        sys.exit(1)
    result = run(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False))