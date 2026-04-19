#!/bin/bash
echo "Installing FastAPI backend dependencies..."
pip install fastapi==0.111.0 "uvicorn[standard]==0.29.0" motor==3.4.0 pymongo==4.7.2 \
    python-multipart==0.0.9 "python-jose[cryptography]==3.3.0" "passlib[bcrypt]==1.7.4" \
    python-dotenv==1.0.1 aiofiles==23.2.1 httpx==0.27.0 "pydantic[email]==2.7.1" pydantic-settings
echo "Done! Start: uvicorn main:app --reload --port 5000"
