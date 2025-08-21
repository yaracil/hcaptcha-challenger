FROM mcr.microsoft.com/playwright/python:v1.52.0-noble
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

USER root
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        xvfb \
        tini \
        wget \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project metadata and source
COPY pyproject.toml README.md requirements-api.txt ./
COPY src ./src

# Install python dependencies
RUN uv pip install --system --no-cache-dir -r requirements-api.txt \
 && uv pip install --system .

ENV HOST=0.0.0.0
ENV PORT=8000

CMD ["uvicorn", "hcaptcha_challenger.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
