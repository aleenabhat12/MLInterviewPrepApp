"""Entry point for the ML Interview Prep mobile app.

Ensures the mobile/ directory is first on sys.path (so mobile/app.py is
found before the root app.py), then appends the project root so the shared
logic modules (config, data_manager, question_generator, scenario_questions)
are importable without copying them into this folder.
"""

import sys
import os

_MOBILE_DIR  = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_MOBILE_DIR)

# mobile/ must come BEFORE the project root so `from app import ...` resolves
# to mobile/app.py rather than the root desktop app.py.
if _MOBILE_DIR not in sys.path:
    sys.path.insert(0, _MOBILE_DIR)

# Project root goes after mobile/ — shared logic modules live here.
if _PROJECT_ROOT not in sys.path:
    sys.path.append(_PROJECT_ROOT)

# Simulate a mobile window size when running on desktop for development
from kivy.config import Config
if os.environ.get("MOBILE_DEV_MODE", "1") == "1":
    Config.set("graphics", "width", "390")
    Config.set("graphics", "height", "844")
    Config.set("graphics", "resizable", "0")

# ── Font registration ─────────────────────────────────────────────────────────
# Register an emoji-capable font so Kivy can render emoji glyphs.
# On Windows: use Segoe UI Emoji (seguiemj.ttf) which ships with Windows 10/11.
# On Android/iOS: the system font already handles emoji; use Roboto as a no-op fallback.
from kivy.core.text import LabelBase
import kivy as _kivy

_SEGOE_EMOJI = r"C:\Windows\Fonts\seguiemj.ttf"
_roboto_path = os.path.join(os.path.dirname(_kivy.__file__), "data", "fonts", "Roboto-Regular.ttf")
_emoji_font  = _SEGOE_EMOJI if os.path.exists(_SEGOE_EMOJI) else _roboto_path
LabelBase.register("EmojiFont", fn_regular=_emoji_font)

# Also register DejaVuSans as the default font — it covers far more BMP symbols
# (gear ⚙, stars ★, arrows ←→, geometric shapes ●▼◎) than Roboto.
_dejavu = os.path.join(os.path.dirname(_kivy.__file__), "data", "fonts", "DejaVuSans.ttf")
if os.path.exists(_dejavu):
    LabelBase.register("Roboto",
                       fn_regular=_dejavu,
                       fn_bold=_dejavu,          # DejaVuSans has no separate bold in Kivy's bundle
                       fn_italic=_dejavu,
                       fn_bolditalic=_dejavu)
# ─────────────────────────────────────────────────────────────────────────────

from app import MLInterviewPrepMobileApp  # noqa: E402

if __name__ == "__main__":
    MLInterviewPrepMobileApp().run()
