from __future__ import annotations

import asyncio
import os

import psutil
from fastapi import FastAPI, HTTPException, Request
from loguru import logger
from pydantic import BaseModel, Field, HttpUrl

from .browser import BrowserProvider
from .solver import solve_challenge

app = FastAPI()

MAX_CONCURRENCY = int(os.getenv("MAX_CONCURRENCY", "5"))
SEMAPHORE = asyncio.Semaphore(MAX_CONCURRENCY)
LOAD_THRESHOLD = float(os.getenv("LOAD_THRESHOLD", "70"))


class SolveRequest(BaseModel):
    cdp_url: str = Field(..., description="WebSocket endpoint for Chrome DevTools")
    target_url: HttpUrl | None = Field(
        default=None, description="Select page whose URL best matches this value"
    )
    timeout: int | None = Field(default=None, description="Optional timeout in seconds")


class SolveResponse(BaseModel):
    token: str
    details: dict


def _under_load() -> bool:
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    logger.debug("CPU %: {cpu}, MEM %: {mem}", cpu=cpu, mem=mem)
    return cpu < LOAD_THRESHOLD and mem < LOAD_THRESHOLD


def _check_api_key(request: Request) -> None:
    api_key = os.getenv("API_KEY")
    if not api_key:
        return
    header_key = request.headers.get("x-api-key")
    if header_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.post("/solve", response_model=SolveResponse)
async def solve(req: SolveRequest, request: Request) -> SolveResponse:
    _check_api_key(request)
    if not _under_load():
        raise HTTPException(status_code=503, detail="Server busy")

    async with SEMAPHORE:
        provider = BrowserProvider()
        try:
            page = await provider.connect_over_cdp(req.cdp_url, req.target_url)
            if req.timeout is not None:
                cr = await asyncio.wait_for(solve_challenge(page), timeout=req.timeout)
            else:
                cr = await solve_challenge(page)
            return SolveResponse(token=cr.c, details=cr.model_dump(by_alias=True))
        except ValueError as exc:
            logger.exception("No matching page")
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except Exception as exc:  # pragma: no cover - network/browser errors
            logger.exception("Solve failed")
            raise HTTPException(status_code=500, detail="Solve failed") from exc
        finally:
            await provider.close()
