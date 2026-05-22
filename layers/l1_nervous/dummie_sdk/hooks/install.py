import os
import stat
from pathlib import Path


HOOK_SOURCE = Path(__file__).resolve().parent / "pre_commit.py"
HOOKS_DIR_NAME = "hooks"
PRE_COMMIT_NAME = "pre-commit"


def find_git_root() -> Path:
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".git").is_dir():
            return parent
    return cwd


def get_hooks_dir() -> Path:
    return find_git_root() / ".git" / HOOKS_DIR_NAME


def is_installed() -> bool:
    hook_path = get_hooks_dir() / PRE_COMMIT_NAME
    return hook_path.exists()


def install(pre_commit_path: Path) -> None:
    git_hooks = get_hooks_dir()
    git_hooks.mkdir(parents=True, exist_ok=True)
    dest = git_hooks / PRE_COMMIT_NAME
    dest.write_text(pre_commit_path.read_text())
    dest.chmod(dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"Pre-commit hook installed: {dest}")


def uninstall() -> None:
    hook_path = get_hooks_dir() / PRE_COMMIT_NAME
    if hook_path.exists():
        hook_path.unlink()
        print(f"Pre-commit hook removed: {hook_path}")
    else:
        print("No pre-commit hook to remove")
