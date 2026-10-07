"""
Start 5 separate versions of the game at the same time.

Each version is its OWN world with its OWN save file, on its OWN web link.

How to use:
    python run_all.py          # or double-click start_5_games.bat

It automatically picks 5 FREE ports (normally 8001-8005, so it never
clashes with a server you already have running), opens the first one in
your browser, and prints all the links.

Press Ctrl+C to stop all the games.

Want friends on your Wi-Fi to join too?  Run it like this instead:

    set GCARDS_HOST=0.0.0.0
    python run_all.py
"""

import os
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COUNT = int(os.environ.get("GCARDS_COUNT", "5"))
BASE_PORT = int(os.environ.get("GCARDS_BASE_PORT", "8001"))


def port_is_free(port: int) -> bool:
    """True if nothing is listening on this port right now."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def find_free_ports(count: int, base: int) -> list:
    ports = []
    port = base
    while len(ports) < count and port < base + 200:
        if port_is_free(port):
            ports.append(port)
        port += 1
    return ports


def local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    # show our messages right away (not buffered)
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    # make sure the game tools are installed
    try:
        import uvicorn  # noqa: F401
    except ImportError:
        print()
        print("=" * 64)
        print("The game tools are not installed yet. Run this first:")
        print(f'  "{sys.executable}" -m pip install -r requirements.txt')
        print("=" * 64)
        return

    host = os.environ.get("GCARDS_HOST", "127.0.0.1")
    share_ip = local_ip()
    shown_host = share_ip if host == "0.0.0.0" else "127.0.0.1"

    ports = find_free_ports(COUNT, BASE_PORT)
    if len(ports) < COUNT:
        print(f"Could only find {len(ports)} free ports (needed {COUNT}). Close some apps and retry.")
        return

    print()
    print(f"Starting {COUNT} versions of the game...")
    print()

    procs = []
    for i, port in enumerate(ports):
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
        print(f"(Friends on your Wi-Fi can use http://{share_ip}:{ports[0]} ... and so on.)")
    else:
        print("(Only this computer can open the links. Set GCARDS_HOST=0.0.0.0 to share them.)")
    print()

    # open the first game in your browser for you
    try:
        import webbrowser
        webbrowser.open(f"http://127.0.0.1:{ports[0]}")
    except Exception:
        pass

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
