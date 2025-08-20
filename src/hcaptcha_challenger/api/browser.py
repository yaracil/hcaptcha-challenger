from __future__ import annotations

from playwright.async_api import Browser, Page, async_playwright


class BrowserProvider:
    """Provide pages from external or internal browsers."""

    def __init__(self) -> None:
        self._playwright = None

    async def connect_over_cdp(self, cdp_url: str) -> Page:
        self._playwright = await async_playwright().start()
        browser: Browser = await self._playwright.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = context.pages[0] if context.pages else await context.new_page()
        return page

    async def launch_internal(self) -> Page:  # pragma: no cover - placeholder for future use
        raise NotImplementedError("Internal browser launch is not implemented yet")

    async def close(self) -> None:
        if self._playwright is not None:
            await self._playwright.stop()
