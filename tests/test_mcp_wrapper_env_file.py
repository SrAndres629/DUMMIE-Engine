import os
import subprocess
from pathlib import Path


ROOT = Path("/media/datasets/DUMMIE Engine")
WRAPPER = ROOT / "scripts" / "mcp_wrapper.sh"


def test_mcp_wrapper_loads_n8n_secrets_from_env_file(tmp_path):
    env_file = tmp_path / "n8n.env"
    env_file.write_text(
        "N8N_API_URL=http://127.0.0.1:5678\n"
        "N8N_BASE_URL=http://127.0.0.1:5678\n"
        "N8N_API_KEY=test-secret\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    env.update(
        {
            "DUMMIE_ROOT": str(ROOT),
            "DUMMIE_N8N_ENV_FILE": str(env_file),
        }
    )

    proc = subprocess.run(
        [
            str(WRAPPER),
            "bash",
            "-lc",
            'printf \'%s|%s|%s\' "$N8N_API_URL" "$N8N_BASE_URL" "$N8N_API_KEY"',
        ],
        text=True,
        capture_output=True,
        check=True,
        env=env,
    )

    assert proc.stdout == "http://127.0.0.1:5678|http://127.0.0.1:5678|test-secret"
