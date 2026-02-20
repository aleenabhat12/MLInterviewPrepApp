"""Home / dashboard screen."""

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screen import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton

from screens.styles import (
    BG, CARD, DANGER, INFO, LEVEL_COLORS, PRIMARY, SUBTEXT, SUCCESS,
    TEXT, WARNING, action_button, auto_label, card_layout,
)
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle


class HomeScreen(Screen):
    """Dashboard: stats summary, level progress, quiz-launch buttons."""

    def on_pre_enter(self, *_):
        """Rebuild the UI every time we return to this screen so stats are fresh."""
        self.clear_widgets()
        self._build()

    # ------------------------------------------------------------------
    def _build(self):
        from data_manager import get_level_progress, get_overall_stats, get_weak_topics
        from config import DIFFICULTY_LEVELS

        progress = get_level_progress()
        stats    = get_overall_stats()

        root = BoxLayout(orientation="vertical")

        # ── Background ─────────────────────────────────────────────────
        with root.canvas.before:
            Color(*BG)
            self._bg_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(
            pos=lambda w, v: setattr(self._bg_rect, "pos", v),
            size=lambda w, v: setattr(self._bg_rect, "size", v),
        )

        # ── Scrollable content ─────────────────────────────────────────
        sv = ScrollView(size_hint=(1, 1))
        content = BoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(14),
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))

        # ── Title ──────────────────────────────────────────────────────
        content.add_widget(auto_label(
            text="🎯 ML Interview Prep",
            font_size=dp(22),
            bold=True,
            halign="center",
            color=TEXT,
        ))

        # ── Level progress card ────────────────────────────────────────
        level_card = card_layout()
        level_name  = progress["level_name"]
        lvl_color   = LEVEL_COLORS.get(progress["current_level"], PRIMARY)
        pts         = progress["level_points"]
        pts_next    = progress["points_to_next"]
        pct         = progress["progress_percent"]

        level_card.add_widget(auto_label(
            text=f"Level: [b][color={_hex(lvl_color)}]{level_name}[/color][/b]",
            font_size=dp(16), markup=True, halign="center",
        ))

        bar = ProgressBar(
            max=100, value=pct,
            size_hint_y=None, height=dp(14),
        )
        level_card.add_widget(bar)

        if progress["is_max_level"]:
            pts_text = "🏆 Max Level Reached!"
        else:
            pts_text = f"{pts} / {pts_next} pts to next level"
        level_card.add_widget(auto_label(text=pts_text, color=SUBTEXT, halign="center"))
        content.add_widget(level_card)

        # ── Stats row ─────────────────────────────────────────────────
        stats_row = BoxLayout(orientation="horizontal", spacing=dp(10),
                               size_hint_y=None, height=dp(80))
        accuracy = f"{stats['accuracy']:.0f}%"
        for label, value, color in [
            ("Accuracy", accuracy, SUCCESS),
            ("Quizzes",  str(stats["total_quizzes"]), PRIMARY),
            ("Points",   str(stats["total_points"]),  WARNING),
        ]:
            box = card_layout(orientation="vertical", padding=dp(10), spacing=dp(4))
            box.size_hint_y = None
            box.height = dp(80)
            box.add_widget(auto_label(text=value, font_size=dp(18), bold=True,
                                       color=color, halign="center"))
            box.add_widget(auto_label(text=label, font_size=dp(11),
                                       color=SUBTEXT, halign="center"))
            stats_row.add_widget(box)
        content.add_widget(stats_row)

        # ── Start quiz section ─────────────────────────────────────────
        content.add_widget(auto_label(
            text="Start a Quiz", font_size=dp(16), bold=True, color=TEXT,
        ))

        self._focus_weak = False  # track toggle state

        focus_toggle = ToggleButton(
            text="🎯  Focus on Weak Areas",
            font_size=dp(14),
            background_normal="",
            background_down="",
            background_color=CARD,
            color=SUBTEXT,
            size_hint_y=None,
            height=dp(44),
        )

        def _on_focus_toggle(btn, state):
            self._focus_weak = (state == "down")
            btn.color = SUCCESS if self._focus_weak else SUBTEXT

        focus_toggle.bind(state=_on_focus_toggle)
        content.add_widget(focus_toggle)

        for label, level, color in [
            ("🟢  Beginner",      "beginner",     SUCCESS),
            ("🟡  Intermediate",  "intermediate", WARNING),
            ("🔴  Advanced",      "advanced",     DANGER),
        ]:
            btn = action_button(label, bg_color=color)
            btn.bind(on_release=lambda _, l=level: self._start_quiz(l))
            content.add_widget(btn)

        # ── Scenario quiz ──────────────────────────────────────────────
        content.add_widget(auto_label(
            text="Challenge Mode", font_size=dp(16), bold=True, color=TEXT,
        ))
        scenario_btn = action_button("🎭  Scenario / Trick Questions", bg_color=INFO)
        scenario_btn.bind(on_release=lambda _: self._start_scenario())
        content.add_widget(scenario_btn)

        # ── Weak topics hint ──────────────────────────────────────────
        weak = get_weak_topics(limit=3)
        if weak:
            weak_card = card_layout(spacing=dp(6))
            weak_card.add_widget(auto_label(
                text="📉 Needs Improvement", font_size=dp(13),
                bold=True, color=DANGER,
            ))
            for w in weak:
                pct_str = f"{w['accuracy'] * 100:.0f}%"
                weak_card.add_widget(auto_label(
                    text=f"• {w['topic']}  ({pct_str})",
                    font_size=dp(12), color=SUBTEXT,
                ))
            content.add_widget(weak_card)

        sv.add_widget(content)
        root.add_widget(sv)
        self.add_widget(root)

    # ------------------------------------------------------------------
    def _start_quiz(self, level: str):
        App.get_running_app().start_quiz(
            level=level, focus_weak=self._focus_weak, scenario=False
        )

    def _start_scenario(self):
        App.get_running_app().start_quiz(
            level="advanced", focus_weak=False, scenario=True
        )


# ── helpers ────────────────────────────────────────────────────────────────────

def _hex(rgba) -> str:
    """Convert a (r, g, b, a) 0–1 tuple to a 6-digit hex string for markup."""
    r, g, b = (int(c * 255) for c in rgba[:3])
    return f"{r:02x}{g:02x}{b:02x}"
