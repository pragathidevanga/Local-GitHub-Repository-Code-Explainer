"""Root entrypoint for Local GitHub Repository Code Explainer.

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure root directory is on Python module search path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from frontend.app import run_streamlit_app

if __name__ == "__main__":
    run_streamlit_app()
