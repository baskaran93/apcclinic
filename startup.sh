#!/bin/bash
echo "Current Directory: $(pwd)"
echo "Directory Contents:"
ls -F
echo "App Directory Contents:"
ls -F app/
export PYTHONPATH=$PYTHONPATH:.
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
