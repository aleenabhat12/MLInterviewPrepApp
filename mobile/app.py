"""Main Kivy application class and screen manager for ML Interview Prep mobile."""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window


class MLInterviewPrepMobileApp(App):
    """Root Kivy application.

    Holds shared quiz state so any screen can read/write it via
    ``App.get_running_app()``.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ── Quiz state ──────────────────────────────────────────────
        self.quiz_level: str = "beginner"
        self.is_scenario_quiz: bool = False
        self.focus_weak_areas: bool = False
        self.current_questions: list = []
        self.user_answers: list = []
        self.quiz_results: dict | None = None

    # ------------------------------------------------------------------
    def build(self):
        self.title = "ML Interview Prep"
        Window.clearcolor = (0.102, 0.102, 0.188, 1)  # #1a1a2e dark bg

        # Import screens here to avoid circular imports at module level
        from screens.home_screen import HomeScreen
        from screens.quiz_screen import QuizScreen
        from screens.results_screen import ResultsScreen
        from screens.review_screen import ReviewScreen
        from screens.settings_screen import SettingsScreen

        self.sm = ScreenManager(transition=SlideTransition())
        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(QuizScreen(name="quiz"))
        self.sm.add_widget(ResultsScreen(name="results"))
        self.sm.add_widget(ReviewScreen(name="review"))
        self.sm.add_widget(SettingsScreen(name="settings"))
        return self.sm

    def on_start(self):
        """After build, redirect to Settings on first run."""
        from settings_manager import is_configured, load_settings, apply_settings
        settings = load_settings()
        apply_settings(settings)          # always push saved values into config
        if not is_configured(settings):
            settings_screen = self.sm.get_screen("settings")
            settings_screen.first_run = True
            self.sm.current = "settings"

    # ------------------------------------------------------------------
    # Navigation helpers called by screens
    # ------------------------------------------------------------------

    def start_quiz(self, level: str, focus_weak: bool = False, scenario: bool = False):
        """Reset state and navigate to the quiz screen."""
        self.quiz_level = level
        self.focus_weak_areas = focus_weak
        self.is_scenario_quiz = scenario
        self.current_questions = []
        self.user_answers = []
        self.quiz_results = None
        self.sm.transition.direction = "left"
        self.sm.current = "quiz"

    def show_results(self, results: dict):
        """Store quiz results and navigate to the results screen."""
        self.quiz_results = results
        self.sm.transition.direction = "left"
        self.sm.current = "results"

    def show_review(self):
        """Navigate to the answer-review screen."""
        self.sm.transition.direction = "left"
        self.sm.current = "review"

    def go_home(self):
        """Navigate back to the home screen."""
        self.sm.transition.direction = "right"
        self.sm.current = "home"

    def go_settings(self):
        """Navigate to the settings screen."""
        self.sm.transition.direction = "left"
        self.sm.current = "settings"
