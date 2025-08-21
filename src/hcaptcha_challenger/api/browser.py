from __future__ import annotations

import asyncio
import sys
from difflib import get_close_matches

from playwright.async_api import Browser, Page, async_playwright


class BrowserProvider:
    """Provide pages from external or internal browsers."""

    def __init__(self) -> None:
        self._playwright = None

    async def connect_over_cdp(self, cdp_url: str, target_url: str | None = None) -> Page:
        """Connect to an external browser via CDP and pick a page.

        If ``target_url`` is provided, choose the existing page whose URL best
        matches ``target_url``. When multiple pages share the same match score,
        the first one is returned. A ``ValueError`` is raised when no page is
        available or when none of them match ``target_url``.
        """

        if sys.platform.startswith("win"):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        self._playwright = await async_playwright().start()
        browser: Browser = await self._playwright.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        pages = context.pages

        if target_url and pages:
            urls = [p.url for p in pages]
            match = get_close_matches(target_url, urls, n=1, cutoff=0.0)
            if match:
                return pages[urls.index(match[0])]
            raise ValueError("No page matching target_url")

        if pages:
            return pages[0]
        return await context.new_page()

    async def launch_internal(self) -> Page:  # pragma: no cover - placeholder for future use
        raise NotImplementedError("Internal browser launch is not implemented yet")

    async def close(self) -> None:
        if self._playwright is not None:
            await self._playwright.stop()
