"""
Start the game server.

The easy way:
  * In Thonny: open THIS file (run.py) and press the green Run button.
  * In a terminal:  python run.py

Then open your web browser at:  http://127.0.0.1:8000
"""

import os
import sys


def main():
    # Check that the game's tools are installed. If not, explain kindly
    # how to install them instead of showing a scary error.
    try:
        import uvicorn  # noqa: F401
    except ImportError:
        print()
        print("=" * 64)
        print("The game needs a few extra tools that are not installed yet.")
        print("Copy the line below, paste it in the terminal, press Enter:")
        print()
        print(f'  "{sys.executable}" -m pip install -r requirements.txt')
        print()
        print("(If you use Thonny: menu Tools -> Manage packages...,")
        print(" search for 'uvicorn' and 'fastapi' and click Install.)")
        print("=" * 64)
        return

    uvicorn.run("server.main:app", host="127.0.0.1",
                port=int(os.environ.get("GCARDS_PORT", "8000")), reload=False)


if __name__ == "__main__":
    main()
