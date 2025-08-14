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
    unixodbc-dev 

# Set Python 3 as the default python command
RUN ln -s /usr/bin/python3 /usr/bin/python

# Download the package to configure the Microsoft repo
RUN curl -sSL -O https://packages.microsoft.com/config/debian/$(grep VERSION_ID /etc/os-release | cut -d '"' -f 2 | cut -d '.' -f 1)/packages-microsoft-prod.deb
# Install the package
RUN dpkg -i packages-microsoft-prod.deb

# Update package list again and install ODBC Driver 17
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && rm -f packages-microsoft-prod.deb && rm -rf /var/lib/apt/lists/*

RUN groupadd -r app && useradd -r -g app -m -d /app -s /bin/bash app

# Create necessary directories with proper permissions
RUN mkdir -p /app/src/logs /app/src/static/files && chown -R app:app /app/src/logs /app/src/static/files

RUN chown -R app:app /app 

# Copy requirements first for better caching
COPY src/requirements.txt .

# Create virtual environment and install dependencies
RUN python3 -m venv /app/venv
RUN /app/venv/bin/pip install --upgrade pip && /app/venv/bin/pip install -r requirements.txt

# Copy application files (only src directory)
COPY src/ /app/src/

# Copy and set up the startup script (do this before changing user)
COPY src/start.sh /app/start.sh
RUN chmod +x /app/start.sh && chown app:app /app/start.sh

# Change ownership of all files to app user
RUN chown -R app:app /app

USER app

# Expose port
EXPOSE 8081

# Default command
CMD ["/app/start.sh"]