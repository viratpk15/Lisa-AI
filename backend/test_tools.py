"""
Jarvis AIOS
-----------
Tool Engine Tests

Tests the tool engine and individual tools.
Uses pathlib.Path relative to this test file to ensure
it works regardless of the current working directory.
"""

from pathlib import Path
from app.Tools.engine import engine

# Path to sample.txt is resolved relative to this test file
_TEST_DIR = Path(__file__).parent.resolve()
_SAMPLE_TXT = _TEST_DIR / "sample.txt"

# Ensure sample.txt exists in the workspace directory
# The file_reader tool reads from Path.cwd() / "workspace"
_WS_DIR = Path.cwd().resolve() / "workspace"
_WS_DIR.mkdir(parents=True, exist_ok=True)
_WS_SAMPLE = _WS_DIR / "sample.txt"
if _SAMPLE_TXT.exists():
    _WS_SAMPLE.write_text(_SAMPLE_TXT.read_text(encoding="utf-8"), encoding="utf-8")


if __name__ == "__main__":
    # Read sample.txt from the workspace directory
    result = engine.execute("file_reader", path="sample.txt")
    print(result)
