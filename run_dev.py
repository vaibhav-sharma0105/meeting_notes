import subprocess
import time
import sys
import os
import signal
import platform

def log(msg):
    print(f"[MeetOps Dev] {msg}")

def check_docker_running():
    try:
        subprocess.run(["docker", "info"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False

def start_db():
    log("Starting Database container...")
    subprocess.run(["docker-compose", "up", "-d", "db"], check=True)

def wait_for_db():
    log("Waiting for Database to be ready...")
    # Simple retry loop for connection
    max_retries = 30
    for i in range(max_retries):
        try:
            # We use docker exec to check if pg_isready is successful inside the container
            res = subprocess.run(
                ["docker-compose", "exec", "-T", "db", "pg_isready", "-U", "user"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if res.returncode == 0:
                log("Database is ready.")
                return True
        except Exception:
            pass
        time.sleep(1)
        sys.stdout.write(".")
        sys.stdout.flush()
    log("\nDatabase failed to become ready in time.")
    return False

def run_processes():
    procs = []

    # 1. Backend
    log("Starting Backend (uvicorn)...")
    env = os.environ.copy()
    env["PYTHONPATH"] = "backend"
    if platform.system() == "Windows":
        # On Windows, we use a new console or just run in parallel
        # Shell=True is often needed on Windows to find executables in venv if not activated explicitly
        # But assuming user has python in path
        backend_cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000"]
    else:
        backend_cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000"]

    # We run from root, but ensure PYTHONPATH is set so imports work
    p_backend = subprocess.Popen(backend_cmd, env=env, cwd=os.getcwd())
    procs.append(p_backend)

    # 2. Frontend
    log("Starting Frontend (next dev)...")
    npm_cmd = "npm.cmd" if platform.system() == "Windows" else "npm"
    p_frontend = subprocess.Popen([npm_cmd, "run", "dev"], cwd="frontend")
    procs.append(p_frontend)

    log("Dev environment running. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
            # Check if any process died
            if p_backend.poll() is not None:
                log("Backend process died.")
                break
            if p_frontend.poll() is not None:
                log("Frontend process died.")
                break
    except KeyboardInterrupt:
        log("Stopping...")
    finally:
        p_backend.terminate()
        p_frontend.terminate()
        log("Stopped.")

def main():
    if not check_docker_running():
        log("Error: Docker is not running. Please start Docker Desktop.")
        sys.exit(1)

    start_db()
    if wait_for_db():
        run_processes()
    else:
        log("Aborting due to DB failure.")

if __name__ == "__main__":
    main()
