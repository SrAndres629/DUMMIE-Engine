import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rehydration import dry_run_rehydration
from models import RehydrationManifest, SourceArtifact


def test_rehydration_dry_run_extracts_candidates_without_mutation():
    manifest = RehydrationManifest(
        manifest_id="rehydrate-1",
        source_provider="obsidian",
        scan_roots=["DUMMIE/Decisions"],
        artifact_kinds=["decision", "lesson"],
        mode="dry_run",
    )
    artifact = SourceArtifact(
        provider="obsidian",
        source_uri="obsidian://DUMMIE/Decisions/OBS-001.md",
        content_type="text/markdown",
        content="# Decision\nUse ports.\n\n## Lesson\nDo not couple L2 to Obsidian.",
        payload_hash="abc123abc123abc123",
        observed_at="2026-04-26T00:00:00Z",
    )

    result = dry_run_rehydration(manifest, [artifact])

    assert result.mutated is False
    assert result.candidate_count == 2
