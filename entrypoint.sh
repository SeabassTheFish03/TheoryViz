#!/bin/bash

# Detect if directory is mounted
if mountpoint -q /app/media/images; then
    echo "Mounted directory detected. Skipping permission changes."
else
    echo "Fixing permissions for /app/media/images..."
    chown -R appuser:appuser /app/media/images
    chmod -R 777 /app/media/images
fi

# Run the main container process
exec "$@"
