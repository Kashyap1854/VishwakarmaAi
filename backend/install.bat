@echo off
echo ============================================
echo  Vishwakarma AI - Python Dependency Installer
echo ============================================
echo.

echo [1/5] Installing icrawler...
pip install icrawler
echo.

echo [2/5] Installing Pillow, numpy, wikipedia, ollama...
pip install Pillow numpy wikipedia ollama
echo.

echo [3/5] Installing PyTorch (CPU version)...
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
echo.

echo [4/5] Installing CLIP...
pip install git+https://github.com/openai/CLIP.git
echo.

echo [5/5] Installing faiss-cpu...
pip install faiss-cpu
echo.

echo ============================================
echo  All dependencies installed!
echo  Next steps:
echo    1. python build_dataset.py
echo    2. python extract_features.py
echo    3. npm install  (in this folder)
echo    4. npm start
echo ============================================
pause
