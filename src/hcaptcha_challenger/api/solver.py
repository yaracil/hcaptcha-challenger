from __future__ import annotations

from hcaptcha_challenger import AgentConfig, AgentV, CaptchaResponse
from playwright.async_api import Page


async def solve_challenge(page: Page) -> CaptchaResponse:
    """Solve hCaptcha challenge on the given page."""
    agent_config = AgentConfig()
    agent = AgentV(page=page, agent_config=agent_config)
    await agent.robotic_arm.click_checkbox()
    await agent.wait_for_challenge()
    if not agent.cr_list:
        raise RuntimeError("Challenge did not produce a CaptchaResponse")
    return agent.cr_list[-1]
