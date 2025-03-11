FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the application in editable mode
RUN pip install --no-cache-dir -e .

# Set default environment variables (can be overridden at runtime)
ENV INPUT_FILE="/var/tmp/m3u/playlist.m3u" \
    OUTPUT_FILE="/var/tmp/m3u/playlist_clean.m3u" \
    LOG_FILE="/var/tmp/m3u/m3uclean.log" \
    STREAM_VALIDATE="false" \
    AGGRESSIVE_CLEAN="false"

# Create directory for mounting volumes
RUN mkdir -p /var/tmp/m3u

# Copy and set permissions for the entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Use the custom entrypoint script
ENTRYPOINT ["docker-entrypoint.sh"]

# Optionally, you can define a default CMD if needed (or leave it empty)
CMD []
