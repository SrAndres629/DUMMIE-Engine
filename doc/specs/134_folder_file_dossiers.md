# Spec 134: Folder and File Dossiers

## Purpose
Generate compact, hierarchical summaries (dossiers) of folders and files to provide context without bulk loading source code.

## Scope
- Generates Folder Dossiers for key structural directories.
- Generates File Dossiers in three tiers: metadata-only, standard, and deep.

## Runtime Behavior
1. Read the `repo_inventory.json`.
2. Generate Folder Dossiers for specified key directories.
3. Generate metadata dossiers for all files.
4. Select high-priority files (e.g., runtime modules with tests) for standard/deep dossiers.
5. Extract Python AST signatures for deep dossiers safely.

## Safety Rules
- Must not use LLM for generation.
- Must restrict standard dossiers to max 100, and deep dossiers to max 40.
