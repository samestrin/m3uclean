FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the application
RUN pip install --no-cache-dir -e .

# Set default environment variables
ENV INPUT_FILE="/var/tmp/m3u/playlist.m3u" \
    OUTPUT_FILE="/var/tmp/m3u/playlist_clean.m3u" \
    LOG_FILE="/var/tmp/m3u/m3uclean.log" \
    STREAM_VALIDATE="false" \
    AGGRESSIVE_CLEAN="false"

# Create directory for mounting volumes
RUN mkdir -p /var/tmp/m3u

# Set the entrypoint
ENTRYPOINT ["python", "-m", "m3uclean.app"]

# Default command (will use environment variables)
CMD ["$INPUT_FILE"]