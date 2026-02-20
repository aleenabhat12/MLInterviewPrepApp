"""Entry point for the ML Interview Prep mobile app.

Adds the project root to sys.path so the shared logic modules
(config, data_manager, question_generator, scenario_questions) are
importable without copying them into this folder.
"""

import sys
import os

# Allow importing shared logic from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Simulate a mobile window size when running on desktop for development
from kivy.config import Config
if os.environ.get("MOBILE_DEV_MODE", "1") == "1":
    Config.set("graphics", "width", "390")
    Config.set("graphics", "height", "844")
    Config.set("graphics", "resizable", "0")

from app import MLInterviewPrepMobileApp  # noqa: E402

if __name__ == "__main__":
    MLInterviewPrepMobileApp().run()
