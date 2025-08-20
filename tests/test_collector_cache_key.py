import re
from unittest.mock import MagicMock

from hcaptcha_challenger.agent.collector import Collector, CollectorConfig
from hcaptcha_challenger.models import CaptchaPayload, RequestType


PROMPTS = ["../etc/passwd", "what?*is>this|prompt"]


def _build_payload(prompt: str) -> CaptchaPayload:
    return CaptchaPayload(
        request_type=RequestType.IMAGE_LABEL_BINARY,
        requester_question={"en": prompt},
    )


def test_create_cache_key_sanitizes_prompt(tmp_path):
    collector = Collector(page=MagicMock(), collector_config=CollectorConfig(dataset_dir=tmp_path))
    for prompt in PROMPTS:
        payload = _build_payload(prompt)
        _, cache_path = collector._create_cache_key(payload)
        rel = cache_path.relative_to(tmp_path)
        # request_type and prompt are separate parts in the path
        request_type_part, prompt_part = rel.parts[:2]
        assert re.fullmatch(r"[A-Za-z0-9_-]+", request_type_part)
        assert re.fullmatch(r"[A-Za-z0-9_-]+", prompt_part)
        assert ".." not in prompt_part
