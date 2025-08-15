# Use Debian 11 (Bullseye) as the base image
FROM debian:12-slim

# Set working directory
WORKDIR /app

# Update package list and install essential tools
RUN  apt-get update && apt-get install -y \
    curl \
    gnupg \
    apt-transport-https \
    python3 \
    python3-venv \
    python3-pip \
    python3-dev \
    unixodbc \
    unixodbc-dev \
    # Dependencies for Python packages that need compilation
    build-essential \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev

# Set Python 3 as the default python command
RUN ln -s /usr/bin/python3 /usr/bin/python

# Download the package to configure the Microsoft repo
RUN curl -sSL -O https://packages.microsoft.com/config/debian/$(grep VERSION_ID /etc/os-release | cut -d '"' -f 2 | cut -d '.' -f 1)/packages-microsoft-prod.deb
# Install the package
RUN dpkg -i packages-microsoft-prod.deb

# Update package list again and install ODBC Driver 17
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && rm -f packages-microsoft-prod.deb && rm -rf /var/lib/apt/lists/*

# Create user and group early
RUN groupadd -r app && useradd -r -g app -m -d /app -s /bin/bash app

# Create necessary directories and set ownership
RUN mkdir -p /app/src/logs /app/src/static/files && \
    chown -R app:app /app

# Copy requirements first for better caching
COPY --chown=app:app src/requirements.txt .

# Create virtual environment as app user with optimized pip installation
USER app
RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip setuptools wheel && \
    /app/venv/bin/pip install --no-cache-dir --compile -r requirements.txt

# Copy application files with correct ownership
COPY --chown=app:app src/ /app/src/

# Create the startup script directly in the image
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'set -e' >> /app/start.sh && \
    echo 'echo "Démarrage de l application Datalys Consulting..."' >> /app/start.sh && \
    echo 'cd /app/src' >> /app/start.sh && \
    echo 'export PYTHONPATH=/app/src:$PYTHONPATH' >> /app/start.sh && \
    echo 'export PORT=8082' >> /app/start.sh && \
    echo 'exec /app/venv/bin/python run.py' >> /app/start.sh && \
    chmod +x /app/start.sh

# Expose port
EXPOSE 8082

# Default command
CMD ["/app/start.sh"]