# Lightweight Python 3.11 base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy uv binary for fast package installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files first (cached for fast rebuilds)
COPY requirements.txt pyproject.toml ./
RUN uv pip install --system -r requirements.txt

# Copy application source code
COPY . .

# Expose port 8000 and run FastAPI
EXPOSE 8000
CMD ["fastapi", "run", "backend/main.py", "--port", "8000", "--host", "0.0.0.0"]