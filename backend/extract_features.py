"""
extract_features.py — Build CLIP feature index from dataset/ folder.
Run once after build_dataset.py to generate monument_index.faiss + labels.npy
"""
import os
import torch
import clip
import numpy as np
import faiss
from PIL import Image

HERE         = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(HERE, "dataset")

# Force CPU — works in Docker without GPU
device = "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
model.eval()

features = []
labels   = []
errors   = 0

print(f"Scanning dataset at: {DATASET_PATH}")
print(f"Using device: {device}")

monument_folders = sorted(os.listdir(DATASET_PATH))
print(f"Found {len(monument_folders)} monument folders\n")

for monument in monument_folders:
    folder = os.path.join(DATASET_PATH, monument)
    if not os.path.isdir(folder):
        continue

    imgs = [f for f in os.listdir(folder)
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]

    count = 0
    for img_name in imgs:
        path = os.path.join(folder, img_name)
        try:
            image = preprocess(Image.open(path).convert("RGB")).unsqueeze(0).to(device)
            with torch.no_grad():
                feature = model.encode_image(image)
            features.append(feature[0].cpu().numpy())
            labels.append(monument)
            count += 1
        except Exception as e:
            errors += 1

    print(f"  {monument}: {count} images indexed")

if not features:
    print("ERROR: No images found. Run build_dataset.py first.")
    exit(1)

features = np.array(features).astype("float32")
dimension = features.shape[1]
print(f"\nBuilding FAISS index: {len(features)} vectors, {dimension}D")

index = faiss.IndexFlatL2(dimension)
index.add(features)

faiss.write_index(index, os.path.join(HERE, "monument_index.faiss"))
np.save(os.path.join(HERE, "labels.npy"), labels)

print(f"\n✅ Done! Indexed {len(features)} images across {len(set(labels))} monuments")
print(f"   Skipped {errors} corrupt/unreadable images")
print("   Files saved: monument_index.faiss, labels.npy")