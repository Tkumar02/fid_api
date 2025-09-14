# Use a lightweight Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY fidelity_api.py .

# Expose the port Render expects
ENV PORT=10000

# Command to run the FastAPI app
CMD ["uvicorn", "fidelity_api:app", "--host", "0.0.0.0", "--port", "10000"]
