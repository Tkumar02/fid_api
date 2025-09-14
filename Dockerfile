# Use Selenium’s Chrome + Chromedriver base image
FROM selenium/standalone-chrome:latest

# Switch to root to install Python
USER root

# Install Python + pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy your application code and requirements
COPY fidelity_api.py requirements.txt ./

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose port (only if your app runs as a web service)
EXPOSE 8080

# Run your script
CMD ["python3", "fidelity_api.py"]
