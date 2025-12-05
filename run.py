# run.py
"""Simple runner to start the server (if you prefer running from a single point)."""
import logging
from .session_entry import server  # noqa: F401

if __name__ == "__main__":
    # recommended to configure logging in your real app
    logging.basicConfig(level=logging.INFO)
    # The server is started by `session_entry` when executed as __main__, but if you
    # want to start programmatically you can keep this file as your CLI entry.
    import uvicorn  # optional, depending on how you run your service
    print("Run your server with the LiveKit CLI entrypoint (session_entry module).")
