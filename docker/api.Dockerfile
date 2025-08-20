FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && \
    uv pip install --system .[server]

COPY . .

ENV HOST=0.0.0.0
ENV PORT=8000

CMD ["uvicorn", "hcaptcha_challenger.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
