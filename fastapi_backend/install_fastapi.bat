@echo off
echo ============================================
echo  Vishwakarma AI — FastAPI Backend Installer
echo ============================================
echo.
echo Installing FastAPI dependencies...
pip install fastapi==0.111.0
pip install "uvicorn[standard]==0.29.0"
pip install motor==3.4.0
pip install pymongo==4.7.2
pip install python-multipart==0.0.9
pip install "python-jose[cryptography]==3.3.0"
pip install "passlib[bcrypt]==1.7.4"
pip install python-dotenv==1.0.1
pip install aiofiles==23.2.1
pip install httpx==0.27.0
pip install "pydantic[email]==2.7.1"
pip install pydantic-settings
echo.
echo ============================================
echo Done! Start with:
echo   uvicorn main:app --reload --port 5000
echo ============================================
pause
