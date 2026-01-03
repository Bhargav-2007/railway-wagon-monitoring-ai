#!/bin/bash

echo "🛑 Stopping existing backend..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 2

echo "🚀 Starting backend..."
cd ~/railway_motion_blur_ai/backend
source ../venv/bin/activate
python -m uvicorn app.main:app --reload
