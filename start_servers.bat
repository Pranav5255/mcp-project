@echo off
echo Starting MCP Server with Inspector support...
start cmd /k python main.py
echo Starting Bee Framework integration server...
start cmd /k python bee_integration.py
echo Servers started! 
echo Main MCP server: http://localhost:8000
echo MCP Inspector URL: http://localhost:8000
echo Bee Framework server: http://localhost:8001