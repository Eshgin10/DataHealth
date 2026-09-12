"""Run both services; stop the container if either service exits."""
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import urllib.request


def main():
    data = Path(os.environ.get("DATA_DIR", "/data"))
    data.mkdir(parents=True, exist_ok=True)
    shutil.copytree("/app/sample-data", data / "sample-data", dirs_exist_ok=True)
    processes = []

    def stop(*_):
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for process in processes:
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
        sys.exit(0)

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        api = subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"], cwd=data)
        processes.append(api)
        for _ in range(60):
            if api.poll() is not None:
                raise RuntimeError("API failed to start")
            try:
                with urllib.request.urlopen("http://127.0.0.1:8000/", timeout=1):
                    break
            except OSError:
                time.sleep(1)
        else:
            raise RuntimeError("API startup timed out")
        processes.append(subprocess.Popen(["node", "/app/frontend/server.js"], env={**os.environ, "HOSTNAME": "0.0.0.0"}))
        while all(process.poll() is None for process in processes):
            time.sleep(1)
        raise RuntimeError("A service stopped unexpectedly")
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for process in processes:
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()


if __name__ == "__main__":
    main()
