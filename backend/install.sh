#!/bin/bash
echo "============================================"
echo " Vishwakarma AI - Python Dependency Installer"
echo "============================================"

echo "[1/5] Installing icrawler..."
pip install icrawler

echo "[2/5] Installing Pillow, numpy, wikipedia, ollama..."
pip install Pillow numpy wikipedia ollama

echo "[3/5] Installing PyTorch (CPU)..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

echo "[4/5] Installing CLIP..."
pip install git+https://github.com/openai/CLIP.git

echo "[5/5] Installing faiss-cpu..."
pip install faiss-cpu

echo ""
echo "============================================"
echo "All done! Now run:"
echo "  python build_dataset.py"
echo "  python extract_features.py"
echo "  npm install && npm start"
echo "============================================"
