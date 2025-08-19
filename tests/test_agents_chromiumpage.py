from DrissionPage import ChromiumPage

from hcaptcha_challenger.agent.collector import Collector
from hcaptcha_challenger.agent.challenger import Challenger


def test_agents_accept_chromium_page():
    """Basic smoke test ensuring agents work with ChromiumPage synchronously."""

    page = ChromiumPage()
    collector = Collector(page)
    challenger = Challenger(page)

    # Ensure the page instances are assigned correctly
    assert collector.page is page
    assert challenger.page is page

