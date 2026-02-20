"""Settings screen — collect and persist Azure OpenAI credentials.

Shown automatically on first launch (when no credentials are saved).
Also reachable from the home screen gear button at any time.

``first_run`` mode hides the Back button so the user must save before
continuing.
"""

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from screens.styles import (
    BG, CARD, DANGER, PRIMARY, SUBTEXT, SUCCESS, TEXT, WARNING,
    action_button, auto_label, card_layout,
)


class SettingsScreen(Screen):
    """Form to view and update Azure OpenAI API settings."""

    #: Set to True before entering the screen to hide the Back button
    first_run: bool = False

    def on_pre_enter(self, *_):
        self.clear_widgets()
        self._build()

    # ------------------------------------------------------------------
    def _build(self):
        from settings_manager import load_settings
        settings = load_settings()

        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*BG)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(
            pos=lambda w, v: setattr(self._bg, "pos", v),
            size=lambda w, v: setattr(self._bg, "size", v),
        )

        sv = ScrollView(size_hint=(1, 1))
        content = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(16),
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))

        # ── Title ──────────────────────────────────────────────────────
        content.add_widget(auto_label(
            text="⚙️  API Settings",
            font_size=dp(22),
            bold=True,
            halign="center",
            color=TEXT,
        ))
        if self.first_run:
            content.add_widget(auto_label(
                text="Enter your Azure OpenAI credentials to get started.",
                font_size=dp(13),
                color=SUBTEXT,
                halign="center",
            ))

        # ── Fields ─────────────────────────────────────────────────────
        fields_card = card_layout(spacing=dp(12))

        self._fields: dict[str, TextInput] = {}

        field_defs = [
            ("azure_openai_endpoint",    "Endpoint URL",
             "https://your-resource.openai.azure.com/", False),
            ("azure_openai_api_key",     "API Key",
             "Your Azure OpenAI API key",               True),
            ("azure_openai_deployment",  "Deployment Name",
             "e.g. gpt-4o",                             False),
            ("azure_openai_api_version", "API Version",
             "2024-08-01-preview",                      False),
        ]

        for key, label, hint, is_password in field_defs:
            fields_card.add_widget(auto_label(
                text=label,
                font_size=dp(13),
                color=SUBTEXT,
            ))
            ti = TextInput(
                text=settings.get(key, ""),
                hint_text=hint,
                password=is_password,
                multiline=False,
                size_hint_y=None,
                height=dp(48),
                font_size=dp(14),
                background_color=(0.12, 0.18, 0.32, 1),
                foreground_color=TEXT,
                hint_text_color=(*SUBTEXT[:3], 0.6),
                cursor_color=TEXT,
                padding=[dp(12), dp(12)],
            )
            fields_card.add_widget(ti)
            self._fields[key] = ti

        content.add_widget(fields_card)

        # ── Status label (feedback after Test / Save) ──────────────────
        self._status_lbl = auto_label(
            text="",
            font_size=dp(13),
            halign="center",
            color=SUBTEXT,
        )
        content.add_widget(self._status_lbl)

        # ── Buttons ────────────────────────────────────────────────────
        test_btn = action_button("🔌  Test Connection", bg_color=PRIMARY)
        test_btn.bind(on_release=lambda _: self._test_connection())
        content.add_widget(test_btn)

        save_btn = action_button("💾  Save Settings", bg_color=SUCCESS)
        save_btn.bind(on_release=lambda _: self._save())
        content.add_widget(save_btn)

        if not self.first_run:
            back_btn = action_button("← Back", bg_color=(0.2, 0.2, 0.3, 1),
                                     height=dp(44))
            back_btn.bind(on_release=lambda _: App.get_running_app().go_home())
            content.add_widget(back_btn)

        sv.add_widget(content)
        root.add_widget(sv)
        self.add_widget(root)

    # ------------------------------------------------------------------
    def _current_values(self) -> dict:
        return {k: ti.text.strip() for k, ti in self._fields.items()}

    def _set_status(self, msg: str, color=SUBTEXT):
        self._status_lbl.color = color
        self._status_lbl.text = msg

    # ------------------------------------------------------------------
    def _test_connection(self):
        """Send a minimal API request to verify the credentials."""
        self._set_status("Testing connection…", SUBTEXT)

        import threading
        threading.Thread(target=self._do_test, daemon=True).start()

    def _do_test(self):
        values = self._current_values()
        endpoint   = values["azure_openai_endpoint"]
        api_key    = values["azure_openai_api_key"]
        deployment = values["azure_openai_deployment"]
        api_version = values["azure_openai_api_version"]

        if not (endpoint and api_key and deployment):
            Clock.schedule_once(lambda _: self._set_status(
                "❌  Fill in Endpoint, API Key and Deployment first.", DANGER))
            return

        try:
            import httpx, json as _json

            if endpoint.rstrip("/").endswith("/v1"):
                url = f"{endpoint.rstrip('/')}/chat/completions"
                headers = {"Authorization": f"Bearer {api_key}",
                           "Content-Type": "application/json"}
            else:
                url = (f"{endpoint.rstrip('/')}/openai/deployments/{deployment}"
                       f"/chat/completions?api-version={api_version}")
                headers = {"api-key": api_key,
                           "Content-Type": "application/json"}

            body = {
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 1,
            }
            resp = httpx.post(url, headers=headers,
                              json=body, timeout=10)
            if resp.status_code in (200, 400):
                # 400 is still a valid auth response (bad request, not unauthorized)
                Clock.schedule_once(lambda _: self._set_status(
                    "✅  Connection successful!", SUCCESS))
            elif resp.status_code == 401:
                Clock.schedule_once(lambda _: self._set_status(
                    "❌  Unauthorized — check your API key.", DANGER))
            elif resp.status_code == 404:
                Clock.schedule_once(lambda _: self._set_status(
                    "❌  Not found — check endpoint / deployment name.", DANGER))
            else:
                Clock.schedule_once(lambda _: self._set_status(
                    f"⚠️  HTTP {resp.status_code} — verify your settings.", WARNING))
        except Exception as exc:
            msg = f"❌  {exc}"
            Clock.schedule_once(lambda _, m=msg: self._set_status(m, DANGER))

    # ------------------------------------------------------------------
    def _save(self):
        from settings_manager import save_settings, apply_settings, is_configured
        values = self._current_values()

        if not is_configured(values):
            self._set_status(
                "⚠️  Endpoint, API Key and Deployment are required.", WARNING)
            return

        save_settings(values)
        apply_settings(values)
        self._set_status("✅  Settings saved!", SUCCESS)

        if self.first_run:
            self.first_run = False
            # Short delay so the user sees the confirmation before navigating
            Clock.schedule_once(
                lambda _: App.get_running_app().go_home(), 1.2)
