from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl


class SolveRequest(BaseModel):
    cdp_url: str = Field(..., description="WebSocket endpoint for Chrome DevTools")
    target_url: HttpUrl | None = Field(
        default=None, description="Select page whose URL best matches this value"
    )
    timeout: int | None = Field(default=None, description="Optional timeout in seconds")

    pre_solve_script: str | None = Field(
        default=None,
        description="JavaScript to run before solving the challenge",
    )
    post_solve_script: str | None = Field(
        default=None,
        description="JavaScript to run after solving the challenge",
    )


class SolveResponse(BaseModel):
    token: str
    details: dict
