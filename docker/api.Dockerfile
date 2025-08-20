FROM python:3.11-slim

WORKDIR /app

# Copy project files and install dependencies from requirements-api.txt
COPY . .
RUN pip install --no-cache-dir -r requirements-api.txt

ENV HOST=0.0.0.0
ENV PORT=8000

CMD ["uvicorn", "hcaptcha_challenger.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
