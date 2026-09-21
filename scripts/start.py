"""Start the backend and frontend development servers."""

from __future__ import annotations

import subprocess
import sys
from shutil import which
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    backend_python = ROOT / "backend" / ".venv" / "Scripts" / "python.exe"
    if not backend_python.exists():
        print("Backend environment is missing. Follow the setup steps in README.md.")
        return 1

    npm = which("npm")
    if npm is None:
        print("npm is missing. Install Node.js and make npm available on PATH.")
        return 1

    processes = [
        subprocess.Popen(
            [
                str(backend_python),
                "-m",
                "uvicorn",
                "app.main:app",
                "--reload",
                "--port",
                "8000",
            ],
            cwd=ROOT / "backend",
        ),
        subprocess.Popen(
            [
                str(backend_python),
                "-m",
                "uvicorn",
                "app.test_mcp_server:app",
                "--reload",
                "--port",
                "8001",
            ],
            cwd=ROOT / "backend",
        ),
        subprocess.Popen(
            [npm, "run", "dev"],
            cwd=ROOT / "frontend",
        ),
    ]

    try:
        return max(process.wait() for process in processes)
    except KeyboardInterrupt:
        for process in processes:
            process.terminate()
        return 0


if __name__ == "__main__":
    sys.exit(main())
