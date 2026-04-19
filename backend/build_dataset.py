"""
build_dataset.py — Download training images for ALL 48 monuments in requirements.json.
Install first: pip install icrawler
"""
import os, sys

try:
    from icrawler.builtin import BingImageCrawler
except ImportError:
    print("ERROR: icrawler not installed. Run: pip install icrawler")
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))

# Every folder name maps to search queries.
# Folder name → LABEL_TO_DB_KEY → requirements.json key  (all three must align)
MONUMENTS = {
    # ── Original 15 (already in index) ───────────────────────────────────────
    "meenakshi_temple":           ["Meenakshi Temple Madurai gopuram", "Meenakshi Amman Temple architecture"],
    "brihadeeswarar_temple":      ["Brihadeeswarar Temple Thanjavur Chola", "Big Temple Thanjavur architecture"],
    "virupaksha_temple":          ["Virupaksha Temple Hampi gopuram", "Hampi Virupaksha temple architecture"],
    "murudeshwar_temple":         ["Murudeshwar Temple Karnataka gopuram", "Murudeshwar Shiva statue temple"],
    "padmanabhaswamy_temple":     ["Padmanabhaswamy Temple Trivandrum exterior", "Padmanabhaswamy temple Kerala gopuram"],
    "tirupati_balaji":            ["Tirupati Balaji Tirumala temple", "Tirumala Venkateswara temple architecture"],
    "chennakesava_temple":        ["Chennakesava Temple Belur Hoysala carvings", "Belur temple Karnataka architecture"],
    "hoysaleswara_temple":        ["Hoysaleswara Temple Halebidu carvings", "Halebidu Hoysala architecture Karnataka"],
    "rameswaram_temple":          ["Ramanathaswamy Temple Rameswaram corridor", "Rameswaram temple long corridor pillars"],
    "shore_temple":               ["Shore Temple Mahabalipuram Pallava", "Mahabalipuram Shore temple sea"],
    "hampi_stone_chariot":        ["Hampi Stone Chariot Vijayanagara", "Vittala temple chariot Karnataka"],
    "konark_sun_temple":          ["Konark Sun Temple Odisha architecture", "Konark temple wheel Kalinga"],
    "qutub_minar":                ["Qutub Minar Delhi minaret", "Qutub Minar complex iron pillar Delhi"],
    "tajmahal":                   ["Taj Mahal Agra white marble", "Taj Mahal Mughal architecture Agra"],
    "gateway_of_india":           ["Gateway of India Mumbai arch", "Gateway of India architecture Mumbai"],

    # ── Mughal / North Indian ─────────────────────────────────────────────────
    "charminar_hyderabad":        ["Charminar Hyderabad four minarets", "Charminar Hyderabad architecture"],
    "red_fort_delhi":             ["Red Fort Delhi Lal Qila Mughal", "Red Fort Delhi walls sandstone"],
    "hawa_mahal":                 ["Hawa Mahal Jaipur palace of winds", "Hawa Mahal pink facade Rajasthan"],
    "humayuns_tomb":              ["Humayun's Tomb Delhi Mughal garden", "Humayuns tomb char bagh Delhi"],
    "fatehpur_sikri":             ["Fatehpur Sikri Buland Darwaza", "Fatehpur Sikri Mughal complex architecture"],
    "jama_masjid_delhi":          ["Jama Masjid Delhi mosque exterior", "Jama Masjid Old Delhi Mughal"],
    "agra_fort":                  ["Agra Fort Uttar Pradesh red sandstone", "Agra Fort Mughal architecture"],

    # ── Rajput / Forts ────────────────────────────────────────────────────────
    "hawa_mahal":                 ["Hawa Mahal Jaipur pink palace", "Hawa Mahal lattice windows Rajasthan"],
    "amber_fort_jaipur":          ["Amber Fort Jaipur hillside palace", "Amer Fort Jaipur Rajput architecture"],
    "mehrangarh_fort_jodhpur":    ["Mehrangarh Fort Jodhpur blue city", "Mehrangarh Fort massive walls Jodhpur"],
    "chittorgarh_fort":           ["Chittorgarh Fort Rajasthan towers", "Chittorgarh fort Vijay Stambha"],
    "golkonda_fort":              ["Golkonda Fort Hyderabad architecture", "Golkonda Fort walls Qutb Shahi"],
    "shaniwar_wada":              ["Shaniwar Wada Pune Maratha fort", "Shaniwar Wada gateway Pune"],

    # ── Buddhist / Jain ───────────────────────────────────────────────────────
    "sanchi_stupa":               ["Sanchi Stupa Buddhist torana gate", "Sanchi great stupa Madhya Pradesh"],
    "ajanta_caves":               ["Ajanta Caves Maharashtra Buddhist paintings", "Ajanta cave exterior rock cut"],
    "ellora_caves":               ["Ellora Caves Kailasa temple rock cut", "Ellora Caves Maharashtra architecture"],
    "khajuraho_temples":          ["Khajuraho Temples Madhya Pradesh Nagara", "Khajuraho Kandariya Mahadeva temple"],

    # ── Dravidian South ───────────────────────────────────────────────────────
    "chidambaram_nataraja_temple":["Chidambaram Nataraja Temple Tamil Nadu", "Chidambaram temple golden roof gopuram"],
    "sri_ranganathaswamy_temple": ["Sri Ranganathaswamy Temple Srirangam gopuram", "Ranganathaswamy temple island Tamil Nadu"],
    "ekambareswarar_temple":      ["Ekambareswarar Temple Kanchipuram gopuram", "Kanchipuram Ekambareswarar Shiva temple"],
    "kanchipuram_kailasanathar":  ["Kanchipuram Kailasanathar Temple Pallava", "Kailasanathar temple sandstone Kanchipuram"],
    "chamundeshwari_temple":      ["Chamundeshwari Temple Mysore hill", "Chamundi Hills temple Karnataka"],
    "guruvayur_temple":           ["Guruvayur Temple Kerala exterior", "Guruvayur Krishna temple gopuram Kerala"],
    "sabarimala_temple":          ["Sabarimala Temple Kerala Ayyappa", "Sabarimala hill shrine Kerala"],
    "sringeri_sharada_peetham":   ["Sringeri Sharada Peetham temple Karnataka", "Sringeri math temple river"],
    "dharmasthala_temple":        ["Dharmasthala Manjunatha Temple Karnataka", "Dharmasthala temple gopuram Karnataka"],
    "kollur_mookambika_temple":   ["Kollur Mookambika Temple Karnataka", "Mookambika temple gopuram Kollur"],
    "kukke_subramanya_temple":    ["Kukke Subramanya Temple Karnataka", "Kukke Subramanya forest temple"],

    # ── Rock-cut / Cave ───────────────────────────────────────────────────────
    "badami_cave_temples":        ["Badami Cave Temples Chalukya Karnataka", "Badami caves sandstone rock cut"],
    "pattadakal_temples":         ["Pattadakal Temples Karnataka Chalukya", "Pattadakal world heritage stone temples"],
    "lepakshi_veerabhadra_temple":["Lepakshi Veerabhadra Temple Andhra hanging pillar", "Lepakshi temple paintings Andhra"],

    # ── Hoysala extras ────────────────────────────────────────────────────────
    "belur_temple_karnataka":     ["Belur Chennakesava Temple Karnataka exterior", "Belur temple Hoysala carvings"],
    "halebidu_temple_karnataka":  ["Halebidu Temple Karnataka exterior", "Halebidu Hoysaleswara temple carvings"],

    # ── Other ─────────────────────────────────────────────────────────────────
    "mysore_palace":              ["Mysore Palace Amba Vilas exterior", "Mysore Palace illuminated Karnataka"],
    "lotus_temple":               ["Lotus Temple Delhi Bahai architecture", "Lotus Temple white petals Delhi"],
    "gol_gumbaz_bijapur":         ["Gol Gumbaz Bijapur dome whispering gallery", "Gol Gumbaz Adil Shah Karnataka"],
    "rani_ki_vav":                ["Rani ki Vav stepwell Patan Gujarat", "Rani ki Vav UNESCO stepwell carvings"],
    "chhatrapati_shivaji_terminus":["Chhatrapati Shivaji Terminus Mumbai Victorian Gothic", "CST Mumbai railway station heritage"],
    "salar_jung_museum":          ["Salar Jung Museum Hyderabad exterior", "Salar Jung Museum building Hyderabad"],
    "raghurajpur_village":        ["Raghurajpur Artist Village Odisha pattachitra", "Raghurajpur heritage village Puri Odisha"],
    "india_gate_delhi":           ["India Gate Delhi war memorial", "India Gate New Delhi arch"],
    "victoria_memorial_kolkata":  ["Victoria Memorial Kolkata white marble", "Victoria Memorial garden Kolkata"],
    "sun_temple_modhera":         ["Sun Temple Modhera Gujarat architecture", "Modhera Sun Temple stepped tank"],
    "rashtrapati_bhavan":         ["Rashtrapati Bhavan New Delhi architecture", "President House India Lutyens Delhi"],
}

# Remove duplicate key (hawa_mahal was listed twice above - fix)
DATASET_DIR = os.path.join(HERE, "dataset")
os.makedirs(DATASET_DIR, exist_ok=True)

total = len(MONUMENTS)
for i, (monument, keywords) in enumerate(MONUMENTS.items(), 1):
    path = os.path.join(DATASET_DIR, monument)
    existing = len([f for f in os.listdir(path)
                    if f.lower().endswith(('.jpg','.jpeg','.png','.webp'))]) if os.path.exists(path) else 0
    if existing >= 50:
        print(f"[{i}/{total}] SKIP {monument} ({existing} images already)")
        continue

    os.makedirs(path, exist_ok=True)
    print(f"\n[{i}/{total}] Downloading: {monument}")
    for keyword in keywords:
        print(f"  → {keyword}")
        try:
            crawler = BingImageCrawler(storage={"root_dir": path})
            crawler.crawl(keyword=keyword, max_num=40)
        except Exception as e:
            print(f"  [error] {e}")

print("\n✅ Dataset download complete. Now run: python3 extract_features.py")