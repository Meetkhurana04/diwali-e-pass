@echo off
echo Starting Diwali E-Pass System...
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting Flask server...
echo Access the application at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py
