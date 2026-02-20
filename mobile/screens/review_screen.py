"""Review screen — scrollable breakdown of every question after a quiz."""

from kivy.app import App
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from screens.styles import (
    BG, CARD, DANGER, PRIMARY, SUBTEXT, SUCCESS, TEXT,
    action_button, auto_label, card_layout, emoji_markup,
)

_OPTION_LABELS = ["A", "B", "C", "D"]


class ReviewScreen(Screen):
    """Shows every question with the user's answer vs the correct answer + explanation."""

    def on_pre_enter(self, *_):
        self.clear_widgets()
        self._build()

    def _build(self):
        app = App.get_running_app()
        questions = app.current_questions
        answers   = app.user_answers

        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*BG)
            bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda w, v: setattr(bg, "pos", v),
                  size=lambda w, v: setattr(bg, "size", v))

        # ── Fixed header ───────────────────────────────────────────────
        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(52),
            padding=(dp(16), dp(8)),
        )
        with header.canvas.before:
            Color(*CARD)
            h_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda w, v: setattr(h_rect, "pos", v),
                    size=lambda w, v: setattr(h_rect, "size", v))

        header.add_widget(Label(
            text="Answer Review",
            font_size=dp(17), bold=True, color=TEXT,
            size_hint_x=0.7, halign="left",
        ))
        back_btn = action_button("Home", bg_color=PRIMARY,
                                  size_hint_x=0.3, height=dp(36))
        back_btn.bind(on_release=lambda _: App.get_running_app().go_home())
        header.add_widget(back_btn)

        root.add_widget(header)

        # ── Scrollable question cards ──────────────────────────────────
        sv = ScrollView(size_hint=(1, 1))
        content = BoxLayout(
            orientation="vertical",
            padding=(dp(12), dp(8)),
            spacing=dp(12),
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))

        for i, (q, user_ans) in enumerate(zip(questions, answers)):
            content.add_widget(self._question_card(i + 1, q, user_ans))

        sv.add_widget(content)
        root.add_widget(sv)
        self.add_widget(root)

    # ------------------------------------------------------------------
    def _question_card(self, num: int, q: dict, user_ans: int) -> BoxLayout:
        correct_ans = q.get("correct_answer", -1)
        is_correct  = (user_ans == correct_ans)
        result_color = SUCCESS if is_correct else DANGER
        result_icon  = "✅" if is_correct else "❌"

        card = card_layout(spacing=dp(8))

        # Question number + result icon
        card.add_widget(auto_label(
            text=emoji_markup(f"{result_icon} [b]Q{num}.[/b]  {q['question']}"),
            font_size=dp(13), markup=True, color=TEXT,
        ))

        # Options: highlight correct green, user-wrong red
        for i, opt in enumerate(q.get("options", [])):
            if i == correct_ans and i == user_ans:
                prefix = emoji_markup("✅ ")
                color  = SUCCESS
            elif i == correct_ans:
                prefix = "✔ "
                color  = SUCCESS
            elif i == user_ans:
                prefix = "✘ "
                color  = DANGER
            else:
                prefix = "   "
                color  = SUBTEXT

            card.add_widget(auto_label(
                text=f"{prefix}{_OPTION_LABELS[i]}.  {opt}",
                font_size=dp(12), color=color, markup=True,
            ))

        # Explanation (collapsed behind a small divider label)
        card.add_widget(auto_label(
            text="Explanation:", font_size=dp(12), bold=True, color=result_color,
        ))
        explanation = q.get("explanation", "").strip()
        card.add_widget(auto_label(
            text=explanation, font_size=dp(12), color=SUBTEXT,
        ))

        return card
