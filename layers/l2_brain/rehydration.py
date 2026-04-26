from dataclasses import dataclass, field

from models import RehydrationManifest, SourceArtifact


@dataclass
class RehydrationCandidate:
    kind: str
    source_uri: str
    text: str


@dataclass
class RehydrationDryRun:
    manifest_id: str
    mutated: bool
    candidates: list[RehydrationCandidate] = field(default_factory=list)

    @property
    def candidate_count(self) -> int:
        return len(self.candidates)


def dry_run_rehydration(
    manifest: RehydrationManifest,
    artifacts: list[SourceArtifact],
) -> RehydrationDryRun:
    candidates: list[RehydrationCandidate] = []
    for artifact in artifacts:
        content_lower = artifact.content.lower()
        if "decision" in manifest.artifact_kinds and "# decision" in content_lower:
            candidates.append(
                RehydrationCandidate("decision", artifact.source_uri, artifact.content)
            )
        if "lesson" in manifest.artifact_kinds and "## lesson" in content_lower:
            candidates.append(
                RehydrationCandidate("lesson", artifact.source_uri, artifact.content)
            )
    return RehydrationDryRun(manifest.manifest_id, mutated=False, candidates=candidates)
