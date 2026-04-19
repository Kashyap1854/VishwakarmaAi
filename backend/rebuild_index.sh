#!/bin/bash
# Run this INSIDE the backend container to rebuild the full 48-monument index
# Usage: docker exec -it vishwakarma-backend bash /backend/rebuild_index.sh

set -e
echo "=========================================="
echo "  Vishwakarma — Full Index Rebuild"
echo "=========================================="

cd /backend

echo ""
echo "Step 1/3: Installing icrawler for dataset download..."
pip install icrawler -q

echo ""
echo "Step 2/3: Downloading images for all 48 monuments..."
echo "         (Skips monuments that already have 50+ images)"
python3 build_dataset.py

echo ""
echo "Step 3/3: Extracting CLIP features and rebuilding FAISS index..."
python3 extract_features.py

echo ""
echo "=========================================="
echo "  ✅ Done! Index rebuilt with all monuments"
echo "  Restart the backend to load new index:"
echo "  docker-compose restart backend"
echo "=========================================="