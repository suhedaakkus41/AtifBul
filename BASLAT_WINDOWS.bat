@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv
    if errorlevel 1 goto hata
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto hata
".venv\Scripts\python.exe" -m streamlit run app.py
if errorlevel 1 goto hata
exit /b 0
:hata
echo Kurulum veya baslatma tamamlanamadi. ONCE_BENI_OKU.md dosyasina bakin.
pause
exit /b 1
