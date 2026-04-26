from dataclasses import dataclass


READ_TOOLS = {
    "obsidian_list_files_in_vault",
    "obsidian_list_files_in_dir",
    "obsidian_get_file_contents",
    "obsidian_simple_search",
    "obsidian_complex_search",
    "obsidian_batch_get_file_contents",
    "obsidian_get_periodic_note",
    "obsidian_get_recent_periodic_notes",
    "obsidian_get_recent_changes",
}

APPEND_WRAPPERS = {
    "knowledge_append_journal_entry",
    "knowledge_export_decision_summary",
    "knowledge_export_lesson",
    "knowledge_export_session_summary",
}

INTERVENTION_TOOLS = {
    "obsidian_patch_content",
    "obsidian_put_content",
    "obsidian_delete_file",
}


@dataclass(frozen=True)
class KnowledgePolicyDecision:
    decision: str
    reason: str


def evaluate_knowledge_operation(
    operation: str,
    wrapper: str | None = None,
) -> KnowledgePolicyDecision:
    if operation in READ_TOOLS:
        return KnowledgePolicyDecision("ALLOWED", "read_only")
    if operation == "obsidian_append_content":
        if wrapper in APPEND_WRAPPERS:
            return KnowledgePolicyDecision("L3_AUTO_APPEND", "append_only_wrapper")
        return KnowledgePolicyDecision("DENY", "append_requires_sovereign_wrapper")
    if operation in INTERVENTION_TOOLS:
        return KnowledgePolicyDecision("L3_INTERVENTION_REQUIRED", "destructive_or_overwrite")
    return KnowledgePolicyDecision("DENY", "unknown_operation")
