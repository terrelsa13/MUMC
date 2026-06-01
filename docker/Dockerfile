FROM docker.io/library/python:3.13-slim

# Set working directory
WORKDIR /usr/src/app

# Copy requirements file
COPY docker/requirements.txt .

# Install Python dependencies
RUN apt-get update && \
    apt-get install -y util-linux && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt

# Create required directories
RUN mkdir -p \
    /usr/src/app/mumc_modules/mumc_defaults \
    /usr/src/app/config \
    /usr/src/app/logs

# Copy application files
COPY mumc_modules/mumc_defaults/*.yaml ./mumc_modules/mumc_defaults/
COPY mumc_modules/*.py ./mumc_modules/
COPY mumc.py .

# Copy execution script
COPY docker/run.sh /run.sh

# Make script executable
RUN chmod +x /run.sh

# Grant ownership to non-root user
RUN chown -R nobody:nogroup /usr/src/app /run.sh

# Better logging behavior for containers
ENV PYTHONUNBUFFERED=1

# Run as non-root
USER nobody:nogroup

# Keep container alive for cron-triggered execution
CMD ["tail", "-f", "/dev/null"]