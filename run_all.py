"""
Start 5 separate versions of the game at the same time.

Each version is its OWN world with its OWN save file, on its OWN web link:

    Game 1  ->  http://127.0.0.1:8000
    Game 2  ->  http://127.0.0.1:8001
    Game 3  ->  http://127.0.0.1:8002
    Game 4  ->  http://127.0.0.1:8003
    Game 5  ->  http://127.0.0.1:8004

How to use:
    python run_all.py

Press Ctrl+C to stop all 5 games.

Want friends on your Wi-Fi to join too?  Run it like this instead:

    set GCARDS_HOST=0.0.0.0
    python run_all.py

Then share links with your local IP (the script prints it).
"""

import os
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COUNT = int(os.environ.get("GCARDS_COUNT", "5"))
BASE_PORT = int(os.environ.get("GCARDS_BASE_PORT", "8000"))


def local_ip() -> str:
    """Try to find this computer's address on the local network."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    host = os.environ.get("GCARDS_HOST", "127.0.0.1")
    share_ip = local_ip()
    shown_host = share_ip if host == "0.0.0.0" else "127.0.0.1"

    print()
    print(f"Starting {COUNT} versions of the game...")
    print()

    procs = []
    for i in range(COUNT):
        port = BASE_PORT + i
        env = os.environ.copy()
        env["GCARDS_PORT"] = str(port)
        env["GCARDS_HOST"] = host
        env["GCARDS_DATA"] = str(ROOT / "data" / f"game{i + 1}")
        proc = subprocess.Popen([sys.executable, str(ROOT / "run.py")], env=env, cwd=str(ROOT))
        procs.append(proc)
        print(f"  Game {i + 1}:  http://{shown_host}:{port}")

    print()
    print("All versions are running. Press Ctrl+C to stop them all.")
    if host == "0.0.0.0":
        print(f"(Friends on your Wi-Fi can use http://{share_ip}:{BASE_PORT} ... and so on.)")
    else:
        print("(Only this computer can open the links. Set GCARDS_HOST=0.0.0.0 to share them.)")
    print()

    try:
        for proc in procs:
            proc.wait()
    except KeyboardInterrupt:
        print("\nStopping all games...")
        for proc in procs:
            proc.terminate()
        for proc in procs:
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
        print("All games stopped.")


if __name__ == "__main__":
    main()
