
from pathlib import Path
import runpy

ROOT_DIR = Path(__file__).resolve().parent

DASHBOARD_FILE = (
    ROOT_DIR
    / "app"
    / "pages"
    / "2_Analytics_Dashboard.py"
)

runpy.run_path(
    str(DASHBOARD_FILE),
    run_name="__main__",
)
