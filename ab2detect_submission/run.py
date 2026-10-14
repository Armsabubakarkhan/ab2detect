"""
AB2DETECT - One-click launcher
Starts FastAPI backend + Streamlit frontend together.

Usage:
    python run.py

Then open: http://localhost:8501
"""

import subprocess
import sys
import os
import time
import threading

BASE = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(BASE, "backend")
FRONTEND = os.path.join(BASE, "frontend")


def run_backend():
    print("[AB2DETECT] Starting backend on http://localhost:8000 ...")
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "api:app",
         "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=BACKEND,
    )


def run_frontend():
    time.sleep(2)  # let backend start first
    print("[AB2DETECT] Starting frontend on http://localhost:8501 ...")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "app.py",
         "--server.port", "8501"],
        cwd=FRONTEND,
    )


if __name__ == "__main__":
    print("=" * 55)
    print("  AB2DETECT - Hallucination Detection System")
    print("  Backend:  http://localhost:8000")
    print("  Frontend: http://localhost:8501")
    print("  API Docs: http://localhost:8000/docs")
    print("=" * 55)

    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()

    run_frontend()  # runs in main thread, blocks until closed
