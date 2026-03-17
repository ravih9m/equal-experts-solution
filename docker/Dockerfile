# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .

# Create virtual environment to keep things clean
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime (Distroless - Secure & Small)
FROM gcr.io/distroless/python3-debian12

# Copy virtual env from builder
COPY --from=builder /opt/venv /opt/venv
COPY app /app/app

# Set Environment
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PORT=8080

# Security: Run as non-root user
USER nonroot

EXPOSE 8080

#ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
# Use the absolute path to the python binary in the venv to run the module
ENTRYPOINT ["/opt/venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]