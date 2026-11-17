@echo off
TITLE AeroSense Flask Backend
COLOR 0A
cd /d "%~dp0"
if exist "aerosense\aerosense" cd aerosense\aerosense
python run_backend.py
pause
