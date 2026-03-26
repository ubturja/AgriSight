"""
conftest.py – project-wide pytest configuration.

Mocks the ``ultralytics`` package at the sys.modules level so that
importing ``ai_pipeline`` never triggers the heavy YOLO model load.
This file is loaded by pytest before any test module is collected.
"""

import sys
import types
from unittest.mock import MagicMock

# Build a lightweight stand-in for the ultralytics package.
_fake_ultralytics = types.ModuleType("ultralytics")

# YOLO must be a *class* (not a plain function) because ai_pipeline
# uses ``YOLO | None`` as a type annotation at module level.
setattr(_fake_ultralytics, "YOLO", MagicMock)  # MagicMock is itself a class

# Force-insert before anything else imports ultralytics
sys.modules["ultralytics"] = _fake_ultralytics
