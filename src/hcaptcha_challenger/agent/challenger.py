"""Simplified synchronous challenger built on top of DrissionPage.

This module provides a minimal subset of the original asynchronous Playwright
implementation.  It is sufficient for unit tests that exercise the high level
API but does not attempt to cover the full feature set of the original
implementation.
"""

from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any, List, Tuple

from loguru import logger
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from DrissionPage import ChromiumPage, DataPacket, ChromiumElement

from hcaptcha_challenger.models import (
    CaptchaPayload,
    CaptchaResponse,
    ChallengeSignal,
    ChallengeTypeEnum,
    RequestType,
)


def _generate_bezier_trajectory(
    start: Tuple[float, float], end: Tuple[float, float], steps: int
) -> List[Tuple[float, float]]:
    """Quadratic Bezier curve used for mouse movements."""

    points: List[Tuple[float, float]] = []
    distance = ((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** 0.5
    offset_factor = min(0.3, max(0.1, distance / 1000))
    mid_x = (start[0] + end[0]) / 2
    mid_y = (start[1] + end[1]) / 2
    control_x = mid_x + random.uniform(-1, 1) * distance * offset_factor
    control_y = mid_y + random.uniform(-1, 1) * distance * offset_factor

    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * start[0] + 2 * (1 - t) * t * control_x + t**2 * end[0]
        y = (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * control_y + t**2 * end[1]
        points.append((x, y))

    return points


class AgentConfig(BaseSettings):
    """Configuration for the synchronous challenger."""

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    GEMINI_API_KEY: SecretStr = Field(default="", description="Create API Key")

    cache_dir: Path = Path("tmp/.cache")
    challenge_dir: Path = Path("tmp/.challenge")
    captcha_response_dir: Path = Path("tmp/.captcha")

    @field_validator("GEMINI_API_KEY", mode="before")
    @classmethod
    def validate_api_key(cls, v: Any) -> str:  # pragma: no cover - simple sanity check
        return str(v or "")


class Challenger:
    """Synchronous challenger implemented with DrissionPage."""

    def __init__(self, page: ChromiumPage, config: AgentConfig | None = None):
        self.page = page
        self.config = config or AgentConfig()
        self.page.listen.start(self._task_handler)

        self.captcha_payload: CaptchaPayload | None = None
        self.captcha_response: CaptchaResponse | None = None

        self._checkbox_selector = (
            "//iframe[starts-with(@src,'https://newassets.hcaptcha.com/captcha/v1/') and "
            "contains(@src, 'frame=checkbox')]"
        )
        self._challenge_selector = (
            "//iframe[starts-with(@src,'https://newassets.hcaptcha.com/captcha/v1/') and "
            "contains(@src, 'frame=challenge')]"
        )

    # ------------------------------------------------------------------ helpers
    @property
    def checkbox_selector(self) -> str:
        return self._checkbox_selector

    @property
    def challenge_selector(self) -> str:
        return self._challenge_selector

    def get_challenge_frame_locator(self) -> ChromiumElement | None:
        return self.page.ele(self.challenge_selector)

    # ------------------------------------------------------------------ mouse
    def click_by_mouse(self, element: ChromiumElement):
        bbox = element.rect
        x = bbox["x"] + bbox["width"] / 2
        y = bbox["y"] + bbox["height"] / 2
        self.page.mouse.move(x, y)
        self.page.mouse.click(x, y)

    def click_checkbox(self):
        element = self.page.ele(self.checkbox_selector)
        if element:
            self.click_by_mouse(element)

    def refresh_challenge(self):
        element = self.page.ele("//div[@class='refresh button']")
        if element:
            self.click_by_mouse(element)

    # ---------------------------------------------------------------- network
    def _task_handler(self, packet: DataPacket):
        if packet.headers.get("content-type", "") == "application/json":
            data = packet.json()
            if data.get("pass"):
                self.captcha_response = CaptchaResponse(**data)
            elif data.get("request_config"):
                self.captcha_payload = CaptchaPayload(**data)

    # ---------------------------------------------------------------- workflow
    def wait_for_challenge(self) -> ChallengeSignal:
        """Very small stub that waits until a captcha is solved or timed out."""

        start_time = time.time()
        while time.time() - start_time < 5:  # 5 seconds sanity wait
            if self.captcha_response:
                return ChallengeSignal.SUCCESS
            time.sleep(0.1)
        return ChallengeSignal.RESPONSE_TIMEOUT

