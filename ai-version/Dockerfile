# AI version (Task 3): multi-stage build — dependencies are installed into a
# virtualenv in the builder, and only that venv + the app are copied to the
# runtime image. Build context is the repository root (see ai-version/compose.yaml).
FROM python:3.11-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /bin/uv
RUN uv venv /opt/venv
COPY requirements.txt .
RUN VIRTUAL_ENV=/opt/venv uv pip install -r requirements.txt

FROM python:3.11-slim
ENV PATH="/opt/venv/bin:$PATH" PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY ai-version/main.py ./main.py
RUN useradd --create-home app
USER app
EXPOSE 8000
CMD ["fastapi", "run", "main.py", "--port", "8000", "--host", "0.0.0.0"]
