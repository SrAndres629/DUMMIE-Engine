from typing import Protocol, runtime_checkable

from models import (
    ConsensusDecision,
    IntentDraft,
    MemoryTemperatureSignal,
    RehydrationManifest,
    SourceArtifact,
)


@runtime_checkable
class KnowledgeProvider(Protocol):
    async def search_context(self, query: str, limit: int = 10) -> list[SourceArtifact]:
        ...

    async def get_artifact(self, source_uri: str) -> SourceArtifact:
        ...


@runtime_checkable
class WisdomPublisher(Protocol):
    async def publish_decision(self, decision: ConsensusDecision) -> str:
        ...

    async def publish_lesson(self, issue: str, correction: str) -> str:
        ...

    async def publish_session_summary(self, session_id: str, summary: str) -> str:
        ...


@runtime_checkable
class EntropyGovernor(Protocol):
    def classify(self, signals: list[MemoryTemperatureSignal]):
        ...


@runtime_checkable
class RehydrationProvider(Protocol):
    def dry_run(self, manifest: RehydrationManifest, artifacts: list[SourceArtifact]):
        ...


@runtime_checkable
class PreflightPublisher(Protocol):
    async def publish_intent_draft(self, draft: IntentDraft) -> str:
        ...
