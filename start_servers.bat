@echo off
echo Starting MCP and Bee servers...

start cmd /k "cd /d %~dp0 && venv\Scripts\activate && python main.py"
timeout /t 5
start cmd /k "cd /d %~dp0 && venv\Scripts\activate && python bee_integration.py"

echo Servers starting...
echo MCP server running on http://localhost:8000
echo Bee integration running on http://localhost:8001