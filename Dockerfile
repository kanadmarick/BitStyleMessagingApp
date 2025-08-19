# Multi-stage build for Python Flask app
FROM python:3.12-slim as builder

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements_docker.txt .

# Install dependencies
RUN pip install --no-cache-dir --user -r requirements_docker.txt

# Production stage
FROM python:3.12-slim

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /root/.local /home/app/.local

# Copy application files
COPY app.py .
COPY index.html .

# Create directory for SQLite database
RUN mkdir -p /app/data && chown -R app:app /app

# Switch to non-root user
USER app

# Make sure scripts in .local are usable
ENV PATH=/home/app/.local/bin:$PATH

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

# Run the application
CMD ["python", "app.py"]
