# Solver API

The solver API connects to an existing Chrome instance over the Chrome DevTools Protocol (CDP) and solves any hCaptcha challenge present on the selected page.

## Endpoint

`POST /solve`

### Request body

```json
{
  "cdp_url": "ws://localhost:9222/devtools/browser/...",
  "target_url": "https://example.com/login",
  "timeout": 120
}
```

- **cdp_url** *(required)* – WebSocket URL of the remote Chrome browser.
- **target_url** *(optional)* – When multiple pages are open, the page whose URL best matches this value is used. If several pages match equally, the first one is chosen.
- **timeout** *(optional, default 120)* – Seconds to wait for the challenge to be solved.

### Response

On success the server returns the hCaptcha token and the raw solver response:

```json
{
  "token": "P1_eyJ0eXAiOiJK...",
  "details": { "...": "..." }
}
```

If the server is busy or a matching page cannot be found, an error response is sent instead:

```json
{"detail": "Server busy"}
```

### Interactive documentation

When running, the FastAPI application exposes Swagger UI at `http://localhost:8000/docs` and a ReDoc view at `/redoc`.

### Docker usage

A ready-to-use image is provided. Build and run with Docker Compose:

```bash
docker compose -f docker/api-compose.yaml up --build
```

Then issue a request:

```bash
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{
        "cdp_url": "ws://browser-host:9222/devtools/browser/...",
        "target_url": "https://example.com/login",
        "timeout": 120
      }'
```

Provide your `GEMINI_API_KEY` via environment variable when starting the container if the solver requires it.

