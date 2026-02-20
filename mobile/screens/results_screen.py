"""Results screen — shown after a quiz is submitted."""

from kivy.app import App
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from screens.styles import (
    BG, CARD, DANGER, INFO, LEVEL_COLORS, PRIMARY, SUBTEXT,
    SUCCESS, TEXT, WARNING, action_button, auto_label, card_layout,
)


class ResultsScreen(Screen):
    """Displays score, points earned, optional level-up banner, and nav buttons."""

    def on_pre_enter(self, *_):
        self.clear_widgets()
        self._build()

    def _build(self):
        app = App.get_running_app()
        results = app.quiz_results or {}
        questions = app.current_questions

        correct  = results.get("correct_count", 0)
        total    = results.get("total_questions", len(questions))
        earned   = results.get("points_earned", 0)
        level_up = results.get("level_up", False)
        new_lvl  = results.get("new_level", app.quiz_level)
        l_pts    = results.get("level_points", 0)
        pts_next = results.get("points_to_next")

        pct = (correct / total * 100) if total else 0
        pct_color = SUCCESS if pct >= 70 else (WARNING if pct >= 40 else DANGER)

        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*BG)
            bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda w, v: setattr(bg, "pos", v),
                  size=lambda w, v: setattr(bg, "size", v))

        sv = ScrollView(size_hint=(1, 1))
        content = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(14),
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))

        # ── Title ──────────────────────────────────────────────────────
        content.add_widget(auto_label(
            text="Quiz Complete! 🎉",
            font_size=dp(22), bold=True, halign="center",
        ))

        # ── Score card ─────────────────────────────────────────────────
        score_card = card_layout()
        score_card.add_widget(auto_label(
            text=f"[b][color={_hex(pct_color)}]{correct} / {total}[/color][/b]",
            font_size=dp(32), halign="center", markup=True,
        ))
        score_card.add_widget(auto_label(
            text=f"{pct:.0f}% correct",
            font_size=dp(16), halign="center", color=pct_color,
        ))
        score_card.add_widget(auto_label(
            text=f"+{earned} points earned",
            font_size=dp(14), halign="center", color=SUBTEXT,
        ))
        content.add_widget(score_card)

        # ── Level-up banner ────────────────────────────────────────────
        if level_up:
            lu_card = card_layout()
            lvl_color = LEVEL_COLORS.get(new_lvl, PRIMARY)
            lu_card.add_widget(auto_label(
                text=f"🏆 Level Up!  →  [b][color={_hex(lvl_color)}]{new_lvl.title()}[/color][/b]",
                font_size=dp(18), halign="center", markup=True,
            ))
            content.add_widget(lu_card)

        # ── Level progress ─────────────────────────────────────────────
        from kivy.uix.progressbar import ProgressBar
        prog_card = card_layout()
        prog_card.add_widget(auto_label(
            text=f"Level: {new_lvl.title()}", font_size=dp(13), color=SUBTEXT,
        ))
        max_val = pts_next or 1
        bar = ProgressBar(
            max=max_val,
            value=min(l_pts, max_val),
            size_hint_y=None,
            height=dp(12),
        )
        prog_card.add_widget(bar)
        pts_label = "Max level reached 🏆" if pts_next is None else f"{l_pts} / {pts_next} pts"
        prog_card.add_widget(auto_label(text=pts_label, color=SUBTEXT, font_size=dp(12)))
        content.add_widget(prog_card)

        # ── Performance hint ───────────────────────────────────────────
        if pct < 50:
            hint = "💡 Keep practicing — review the explanations below to improve!"
        elif pct < 80:
            hint = "👍 Good effort! Review the questions you missed."
        else:
            hint = "⭐ Excellent work! Keep it up."
        content.add_widget(auto_label(text=hint, font_size=dp(13), color=SUBTEXT, halign="center"))

        # ── Action buttons ─────────────────────────────────────────────
        review_btn = action_button("📋  Review Answers", bg_color=INFO)
        review_btn.bind(on_release=lambda _: App.get_running_app().show_review())
        content.add_widget(review_btn)

        home_btn = action_button("🏠  Back to Home", bg_color=PRIMARY)
        home_btn.bind(on_release=lambda _: App.get_running_app().go_home())
        content.add_widget(home_btn)

        sv.add_widget(content)
        root.add_widget(sv)
        self.add_widget(root)


def _hex(rgba) -> str:
    r, g, b = (int(c * 255) for c in rgba[:3])
    return f"{r:02x}{g:02x}{b:02x}"
