from icrawler.builtin import BingImageCrawler
import os

monuments = [
"Taj Mahal",
"Qutub Minar",
"Charminar",
"Hawa Mahal",
"Mysore Palace",
"Gateway of India",
"Lotus Temple",
"Red Fort Delhi",
"Konark Sun Temple",
"Rani ki Vav",
"Humayun's Tomb",
"Fatehpur Sikri",
"Sanchi Stupa",
"Jama Masjid Delhi",    
"Salar Jung Museum",
"Shaniwar Wada",
"Chhatrapati Shivaji Terminus",
"Golkonda Fort",
"Raghurajpur Artist Village",
"Chittorgarh Fort",

"Meenakshi Temple Madurai",
"Brihadeeswarar Temple Thanjavur",
"Virupaksha Temple Hampi",
"Chennakesava Temple Belur",
"Hoysaleswara Temple Halebidu",
"Ramanathaswamy Temple Rameswaram",
"Tirupati Balaji Temple",
"Padmanabhaswamy Temple Trivandrum",
"Sri Ranganathaswamy Temple Srirangam",
"Murudeshwar Temple Karnataka",
"Kanchipuram Kailasanathar Temple",
"Ekambareswarar Temple Kanchipuram",
"Chidambaram Nataraja Temple",
"Sringeri Sharada Peetham",
"Kukke Subramanya Temple",
"Dharmasthala Manjunatha Temple",
"Chamundeshwari Temple Mysore",
"Kollur Mookambika Temple",
"Guruvayur Temple Kerala",
"Sabarimala Temple Kerala",

"Hampi Stone Chariot",
"Lepakshi Veerabhadra Temple",
"Belur Temple Karnataka",
"Halebidu Temple Karnataka",
"Mahabalipuram Shore Temple",
"Gol Gumbaz Bijapur",
"Badami Cave Temples",
"Pattadakal Temples"
]

os.makedirs("dataset", exist_ok=True)

for monument in monuments:

    folder = monument.lower().replace(" ", "_")

    path = f"dataset/{folder}"

    print("Downloading images for:", monument)

    crawler = BingImageCrawler(storage={'root_dir': path})

    crawler.crawl(keyword=monument, max_num=100)

print("Dataset download complete!")