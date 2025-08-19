"""Minimal package initialisation for tests."""

from .agent.challenger import Challenger, AgentConfig
from .agent.collector import Collector, CollectorConfig

__all__ = [
    "Challenger",
    "AgentConfig",
    "Collector",
    "CollectorConfig",
]

