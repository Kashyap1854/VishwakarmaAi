"""
search.py — CLIP + FAISS visual monument search
Requires: monument_index.faiss and labels.npy (from extract_features.py)
"""
import os
import numpy as np
import torch
import clip
import faiss
from PIL import Image

HERE        = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH  = os.path.join(HERE, "monument_index.faiss")
LABELS_PATH = os.path.join(HERE, "labels.npy")

_model      = None
_preprocess = None
_index      = None
_labels     = None

def _load():
    global _model, _preprocess, _index, _labels
    if _model is None:
        _model, _preprocess = clip.load("ViT-B/32", device="cpu")
    if _index is None:
        if not os.path.exists(INDEX_PATH):
            raise FileNotFoundError(
                f"FAISS index not found at {INDEX_PATH}. "
                "Run extract_features.py first."
            )
        _index  = faiss.read_index(INDEX_PATH)
        _labels = np.load(LABELS_PATH, allow_pickle=True)

def search_image(query_path):
    _load()
    image = _preprocess(Image.open(query_path).convert("RGB")).unsqueeze(0)
    with torch.no_grad():
        feature = _model.encode_image(image)
    feature = feature.cpu().numpy().astype("float32")
    distances, indices = _index.search(feature, 1)
    return str(_labels[indices[0][0]])
