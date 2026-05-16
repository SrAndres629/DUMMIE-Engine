# Folder Notes System (P9)

This directory stores governed FolderNotes and NotePlans.

## Rules
- Notes are derived artifacts and cannot override canonical sources.
- Default token role is `summary_only`.
- Notes must be refreshed when source hashes change.
- Use `folder_notes_manifest.json` as the entrypoint.

## Layout
- `folders/<folder_id>/notes.md`
- `folders/<folder_id>/noteplan.md`
- `../folder_notes_manifest.json`
