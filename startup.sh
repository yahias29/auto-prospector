#!/bin/bash

# Get the full path to the certifi certificate bundle
CERT_PATH=$(python -m certifi)

# Start the gunicorn server and tell it to use these certificates
gunicorn --certfile="$CERT_PATH" -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:${PORT} app.main:app