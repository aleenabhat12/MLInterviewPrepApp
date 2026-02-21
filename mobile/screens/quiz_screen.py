"""Quiz screen — loads questions then steps through them one at a time."""

import threading
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from screens.styles import (
    BG, CARD, DANGER, OPTION_BG, PRIMARY, SELECTED_BG, SUBTEXT,
    SUCCESS, TEXT, WARNING, action_button, auto_label, card_layout,
)

_OPTION_LABELS = ["A", "B", "C", "D"]


class QuizScreen(Screen):
    """Loads questions in a background thread, then presents them one by one."""

    def on_pre_enter(self, *_):
        self.clear_widgets()
        self._build_loading()
        self._selected_idx = -1
        self._q_idx = 0
        self._option_btns: list[Button] = []
        threading.Thread(target=self._load_questions, daemon=True).start()

    # ------------------------------------------------------------------
    # Loading state
    # ------------------------------------------------------------------

    def _build_loading(self):
        root = _bg_root()
        lbl = Label(
            text="Loading questions…",
            font_size=dp(16),
            color=TEXT,
            halign="center",
        )
        root.add_widget(lbl)
        self.add_widget(root)

    def _load_questions(self):
        app = App.get_running_app()
        try:
            if app.is_scenario_quiz:
                from question_generator import generate_scenario_questions
                questions = generate_scenario_questions(num_questions=5)
            else:
                from question_generator import generate_questions
                from data_manager import get_weak_topics
                weak = [w["topic"] for w in get_weak_topics()] if app.focus_weak_areas else None
                questions = generate_questions(
                    level=app.quiz_level,
                    focus_weak_areas=app.focus_weak_areas,
                    weak_topics=weak,
                )
            app.current_questions = questions
            Clock.schedule_once(self._on_loaded)
        except Exception as exc:
            Clock.schedule_once(lambda _, e=exc: self._show_error(str(e)))

    def _on_loaded(self, *_):
        app = App.get_running_app()
        if not app.current_questions:
            self._show_error("No questions were generated. Check your API credentials.")
            return
        self._q_idx = 0
        self._show_question()

    def _show_error(self, msg: str):
        self.clear_widgets()
        root = _bg_root()
        root.add_widget(auto_label(
            text=f"⚠ Error\n\n{msg}",
            font_size=dp(14), color=DANGER, halign="center",
        ))
        btn = action_button("← Back", bg_color=CARD)
        btn.bind(on_release=lambda _: App.get_running_app().go_home())
        root.add_widget(btn)
        self.add_widget(root)

    # ------------------------------------------------------------------
    # Question UI
    # ------------------------------------------------------------------

    def _show_question(self):
        self.clear_widgets()
        app = App.get_running_app()
        questions = app.current_questions
        q = questions[self._q_idx]
        total = len(questions)

        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        with root.canvas.before:
            Color(*BG)
            bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda w, v: setattr(bg, "pos", v),
                  size=lambda w, v: setattr(bg, "size", v))

        # ── Header row ─────────────────────────────────────────────────
        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(36))
        header.add_widget(Label(
            text=f"Question {self._q_idx + 1} / {total}",
            font_size=dp(13), color=SUBTEXT,
            size_hint_x=0.5, halign="left",
        ))
        topic = q.get("topic", "")
        header.add_widget(Label(
            text=topic,
            font_size=dp(11), color=SUBTEXT,
            size_hint_x=0.5, halign="right",
        ))
        root.add_widget(header)

        # ── Progress bar ───────────────────────────────────────────────
        bar = ProgressBar(
            max=total, value=self._q_idx + 1,
            size_hint_y=None, height=dp(6),
        )
        root.add_widget(bar)

        # ── Scenario text (if present) ─────────────────────────────────
        if "scenario" in q and q["scenario"]:
            sv_scenario = ScrollView(size_hint=(1, None), height=dp(100))
            scenario_box = BoxLayout(
                orientation="vertical", size_hint_y=None, padding=dp(10)
            )
            scenario_box.bind(minimum_height=scenario_box.setter("height"))
            lbl = auto_label(
                text=q["scenario"].strip(),
                font_size=dp(12), color=SUBTEXT,
            )
            scenario_box.add_widget(lbl)
            sv_scenario.add_widget(scenario_box)
            _add_card_bg(sv_scenario)
            root.add_widget(sv_scenario)

        # ── Question text ──────────────────────────────────────────────
        sv_q = ScrollView(size_hint=(1, None), height=dp(90))
        q_box = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(8))
        q_box.bind(minimum_height=q_box.setter("height"))
        q_box.add_widget(auto_label(
            text=q["question"], font_size=dp(15), bold=True, color=TEXT,
        ))
        sv_q.add_widget(q_box)
        root.add_widget(sv_q)

        # ── Answer options ─────────────────────────────────────────────
        self._selected_idx = -1
        self._option_btns = []
        options_box = BoxLayout(
            orientation="vertical", spacing=dp(8), size_hint_y=None
        )
        options_box.bind(minimum_height=options_box.setter("height"))

        for i, opt_text in enumerate(q["options"]):
            btn = Button(
                text=f"  {_OPTION_LABELS[i]}.  {opt_text}",
                font_size=dp(13),
                color=TEXT,
                halign="left",
                valign="middle",
                background_color=OPTION_BG,
                background_normal="",
                background_down="",
                size_hint_y=None,
                height=dp(56),
            )
            btn.bind(width=lambda w, v: setattr(w, "text_size", (v - dp(16), None)))
            btn.bind(on_release=lambda b, idx=i: self._select_option(idx))
            self._option_btns.append(btn)
            options_box.add_widget(btn)

        options_box.height = len(q["options"]) * (dp(56) + dp(8))
        root.add_widget(options_box)

        # ── Next / Submit button ───────────────────────────────────────
        is_last = (self._q_idx == total - 1)
        self._next_btn = action_button(
            "Submit Quiz" if is_last else "Next  →",
            bg_color=PRIMARY,
        )
        self._next_btn.disabled = True
        self._next_btn.bind(on_release=lambda _: self._advance())
        root.add_widget(self._next_btn)

        self.add_widget(root)

    def _select_option(self, idx: int):
        self._selected_idx = idx
        for i, btn in enumerate(self._option_btns):
            btn.background_color = SELECTED_BG if i == idx else OPTION_BG
        self._next_btn.disabled = False

    def _advance(self):
        App.get_running_app().user_answers.append(self._selected_idx)
        self._q_idx += 1
        app = App.get_running_app()
        if self._q_idx >= len(app.current_questions):
            self._finish_quiz()
        else:
            self._show_question()

    def _finish_quiz(self):
        from data_manager import record_quiz_result
        app = App.get_running_app()
        results = record_quiz_result(
            app.current_questions, app.user_answers, app.quiz_level
        )
        app.show_results(results)


# ── helpers ────────────────────────────────────────────────────────────────────

def _bg_root() -> BoxLayout:
    root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(16))
    with root.canvas.before:
        Color(*BG)
        bg = Rectangle(pos=root.pos, size=root.size)
    root.bind(pos=lambda w, v: setattr(bg, "pos", v),
              size=lambda w, v: setattr(bg, "size", v))
    return root


def _add_card_bg(widget):
    """Add a rounded card background to any widget via canvas.before."""
    def _draw(w, *_):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*CARD)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(8)])
    widget.bind(pos=_draw, size=_draw)
