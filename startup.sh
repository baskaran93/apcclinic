#!/bin/bash
echo "Current Directory: $(pwd)"
echo "Directory Contents:"
ls -F
echo "App Directory Contents:"
ls -F app/

# Kill process on port 8000 if it exists
PIDS=$(lsof -ti:8000)
if [ ! -z "$PIDS" ]; then
  echo "Killing processes on port 8000: $PIDS"
  kill -9 $PIDS
  sleep 5
fi

export PYTHONPATH=$PYTHONPATH:.
./bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
