# Use the slim Python 3.11 image to keep the container footprint small
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements first so Docker caches the install layer
COPY requirements.txt .

# Install all Python dependencies without caching pip downloads
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code into the container
COPY src/ ./src/

# Create a non-root user for security — running as root in containers is bad practice
RUN useradd --create-home appuser

# Switch to the non-root user for all subsequent commands
USER appuser

# Start the MCP server on all interfaces so Docker port mapping works
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]
