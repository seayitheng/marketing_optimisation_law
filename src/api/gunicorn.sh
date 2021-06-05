#!/bin/bash
# This script launches gunicorn WSGI
gunicorn -w 4 -k uvicorn.workers.UvicornWorker --worker-tmp-dir /dev/shm -b 0.0.0.0:3000 src.wisgi:app --preload --timeout 120