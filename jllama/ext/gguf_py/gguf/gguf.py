# This file left for compatibility. If you want to use the GGUF API from Python
# then don't import gguf_py/gguf_py.py directly. If you're looking for examples, see the
# examples/ directory for gguf-py

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Compatibility for people trying to import gguf_py/gguf.py directly instead of as a package.
importlib.invalidate_caches()
import gguf  # noqa: E402

importlib.reload(gguf)
