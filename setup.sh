#!/bin/bash

# Create the /app/tmp directory if it doesn't exist.
# Gradio client often saves temporary files in a /tmp-like location.
# Render's default working directory is /opt/render/project/src/, but /tmp/
# or similar paths might be needed for internal Gradio operations.
# Let's create a specific writable directory inside the project for safety.
mkdir -p /opt/render/project/src/tmp/gradio_files
echo "Created /opt/render/project/src/tmp/gradio_files directory."

# If the TTS model attempts to save files in /tmp/ (which it often does by default),
# and /tmp/ is not directly writable in a way that allows subsequent reads,
# it can cause issues. A common solution for Gradio is to ensure a writable temp dir.
# However, for `gradio_client`, it often uses `tempfile` which should handle it.
# The primary reason for `setup.sh` with Gradio client is usually to install ffmpeg
# or other system dependencies if the TTS model requires them for audio processing.
# Since this TTS model is remote (Gradio Cloud), it handles its own backend.
# The `mkdir` above is a preemptive measure if the client tries to save something
# locally and needs a specific path, but for most Gradio client uses, it's not strictly necessary.
# However, it doesn't hurt to have a robust setup.
