"""Shared color constants and lightweight widget factories for the mobile UI."""

import re
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle

# ── Color palette (R, G, B, A  in 0–1 range) ─────────────────────────────────
BG           = (0.102, 0.102, 0.188, 1)   # #1a1a2e  background
CARD         = (0.086, 0.129, 0.243, 1)   # #16213e  card surface
PRIMARY      = (0.325, 0.204, 0.514, 1)   # #533483  purple action
SUCCESS      = (0.157, 0.655, 0.271, 1)   # #28a745  green / beginner
WARNING      = (0.800, 0.600, 0.020, 1)   # #ffc107  yellow / intermediate
DANGER       = (0.863, 0.204, 0.271, 1)   # #dc3545  red / advanced / wrong
INFO         = (0.059, 0.204, 0.376, 1)   # #0f3460  dark blue accent
TEXT         = (0.878, 0.878, 0.878, 1)   # #e0e0e0  primary text
SUBTEXT      = (0.600, 0.600, 0.600, 1)   # muted text
OPTION_BG    = (0.150, 0.200, 0.350, 1)   # unselected answer option
SELECTED_BG  = (0.200, 0.350, 0.600, 1)   # selected answer option (blue)

LEVEL_COLORS = {
    "beginner":     SUCCESS,
    "intermediate": WARNING,
    "advanced":     DANGER,
}


# ── Emoji rendering ───────────────────────────────────────────────────────────
# Characters in the supplementary planes (U+10000+) are modern colour emoji.
# Kivy's default Roboto font has no glyphs for them; we wrap them in a
# [font=EmojiFont] markup tag so Kivy uses the registered emoji font instead.
_SUPP_EMOJI = re.compile(r'[\U00010000-\U0010FFFF]', flags=re.UNICODE)


def emoji_markup(text: str) -> str:
    """Wrap supplementary-plane emoji in EmojiFont markup tags."""
    return _SUPP_EMOJI.sub(lambda m: f"[font=EmojiFont]{m.group()}[/font]", text)


# ── Widget factories ──────────────────────────────────────────────────────────

def card_layout(orientation="vertical", padding=dp(16), spacing=dp(10), **kwargs):
    """BoxLayout with a rounded dark card background."""
    layout = BoxLayout(
        orientation=orientation,
        padding=padding,
        spacing=spacing,
        size_hint_y=None,
        **kwargs,
    )
    layout.bind(minimum_height=layout.setter("height"))

    def _redraw(w, *_):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*CARD)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(12)])

    layout.bind(pos=_redraw, size=_redraw)
    return layout


def auto_label(text="", font_size=None, color=TEXT, bold=False, halign="left", **kwargs):
    """Label that auto-sizes its height to fit wrapped text."""
    lbl = Label(
        text=text,
        font_size=font_size or dp(14),
        color=color,
        bold=bold,
        halign=halign,
        valign="top",
        size_hint_y=None,
        **kwargs,
    )
    lbl.bind(texture_size=lambda w, s: setattr(w, "height", s[1]))
    lbl.bind(width=lambda w, v: setattr(w, "text_size", (v, None)))
    return lbl


def emoji_label(text="", font_size=None, color=TEXT, bold=False, halign="left", **kwargs):
    """Like auto_label but applies EmojiFont markup for emoji characters.

    Use this for static UI strings that contain emoji.  Do NOT use it for
    dynamic content (e.g. quiz questions) that may contain literal brackets.
    """
    return auto_label(
        text=emoji_markup(text),
        font_size=font_size,
        color=color,
        bold=bold,
        halign=halign,
        markup=True,
        **kwargs,
    )


def action_button(text, bg_color=PRIMARY, height=dp(52), font_size=None, **kwargs):
    """Styled action button — automatically renders emoji via EmojiFont markup."""
    return Button(
        text=emoji_markup(text),
        markup=True,
        font_size=font_size or dp(15),
        bold=True,
        color=TEXT,
        background_color=bg_color,
        background_normal="",
        background_down="",
        size_hint_y=None,
        height=height,
        **kwargs,
    )
