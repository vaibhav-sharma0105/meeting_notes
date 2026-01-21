@echo off
echo Starting MeetOps Database...
docker-compose up -d db
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to start database. Is Docker Desktop running?
    pause
    exit /b %ERRORLEVEL%
)
echo Database started successfully.
echo You can now run the backend with: cd backend && python -m uvicorn main:app --reload
pause
