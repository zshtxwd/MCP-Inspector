"""启动后端和前端开发服务器。"""

from __future__ import annotations

import subprocess
import sys
from shutil import which
from pathlib import Path


# 用于解析后端和前端工作目录的项目根目录。
ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """启动后端、测试 MCP 服务和前端开发进程。"""

    # 后端虚拟环境中的 Python 可执行文件。
    backend_python = ROOT / "backend" / ".venv" / "Scripts" / "python.exe"
    if not backend_python.exists():
        print("Backend environment is missing. Follow the setup steps in README.md.")
        return 1

    # 从当前 PATH 中查找到的 npm 可执行文件。
    npm = which("npm")
    if npm is None:
        print("npm is missing. Install Node.js and make npm available on PATH.")
        return 1

    # 组成本地开发环境的子进程列表。
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
        # 返回父进程观察到的进程退出码。
        return max(process.wait() for process in processes)
    except KeyboardInterrupt:
        # 开发者中断启动器时，终止所有子进程。
        for process in processes:
            process.terminate()
        return 0


if __name__ == "__main__":
    sys.exit(main())
