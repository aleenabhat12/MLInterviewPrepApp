"""Settings screen — provider selector + credential form.

Supports three AI providers:
  • Azure OpenAI  (default)
  • OpenAI        (api.openai.com)
  • Ollama        (local / self-hosted)

Shown automatically on first launch when no credentials are saved.
Reachable at any time via the ⚙️ button on the home screen.
``first_run`` mode hides the Back button so the user must Save first.
"""

import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from screens.styles import (
    BG, CARD, DANGER, INFO, PRIMARY, SUBTEXT, SUCCESS, TEXT, WARNING,
    action_button, auto_label, card_layout, emoji_label, emoji_markup,
)

# Map display label → internal key
_PROVIDER_LABELS = {
    "Azure OpenAI":   "azure",
    "OpenAI":         "openai",
    "Ollama (Local)": "ollama",
}
_PROVIDER_KEYS = {v: k for k, v in _PROVIDER_LABELS.items()}


def _text_input(text="", hint="", password=False) -> TextInput:
    return TextInput(
        text=text,
        hint_text=hint,
        password=password,
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


class SettingsScreen(Screen):
    """Provider selector + credential form."""

    first_run: bool = False

    def on_pre_enter(self, *_):
        self.clear_widgets()
        self._build()

    # ------------------------------------------------------------------
    def _build(self):
        from settings_manager import load_settings
        self._settings = load_settings()
        self._current_provider = self._settings.get("ai_provider", "azure")
        self._fields: dict[str, TextInput] = {}

        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*BG)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(
            pos=lambda w, v: setattr(self._bg, "pos", v),
            size=lambda w, v: setattr(self._bg, "size", v),
        )

        sv = ScrollView(size_hint=(1, 1))
        self._content = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(16),
            size_hint_y=None,
        )
        self._content.bind(minimum_height=self._content.setter("height"))

        # ── Title ──────────────────────────────────────────────────────
        self._content.add_widget(emoji_label(
            text="⚙️  Settings",
            font_size=dp(22), bold=True, halign="center", color=TEXT,
        ))
        if self.first_run:
            self._content.add_widget(auto_label(
                text="Choose a provider and enter your credentials to get started.",
                font_size=dp(13), color=SUBTEXT, halign="center",
            ))

        # ── Provider selector ──────────────────────────────────────────
        provider_card = card_layout(spacing=dp(10))
        provider_card.add_widget(auto_label(
            text="AI Provider", font_size=dp(13), color=SUBTEXT,
        ))

        spinner_label = _PROVIDER_KEYS.get(self._current_provider, "Azure OpenAI")
        self._provider_spinner = Spinner(
            text=spinner_label,
            values=list(_PROVIDER_LABELS.keys()),
            size_hint_y=None,
            height=dp(48),
            font_size=dp(15),
            background_color=PRIMARY,
            color=TEXT,
            background_normal="",
            background_down="",
        )
        self._provider_spinner.bind(text=self._on_provider_change)
        provider_card.add_widget(self._provider_spinner)
        self._content.add_widget(provider_card)

        # ── Provider description ───────────────────────────────────────
        self._desc_lbl = auto_label(
            text=self._provider_description(self._current_provider),
            font_size=dp(12), color=SUBTEXT, halign="left",
        )
        self._content.add_widget(self._desc_lbl)

        # ── Credential fields (dynamic) ────────────────────────────────
        self._cred_card = card_layout(spacing=dp(10))
        self._rebuild_cred_fields(self._current_provider)
        self._content.add_widget(self._cred_card)

        # ── Status label ───────────────────────────────────────────────
        self._status_lbl = auto_label(
            text="", font_size=dp(13), halign="center", color=SUBTEXT,
        )
        self._content.add_widget(self._status_lbl)

        # ── Buttons ────────────────────────────────────────────────────
        test_btn = action_button("🔌  Test Connection", bg_color=INFO)
        test_btn.bind(on_release=lambda _: self._test_connection())
        self._content.add_widget(test_btn)

        save_btn = action_button("💾  Save Settings", bg_color=SUCCESS)
        save_btn.bind(on_release=lambda _: self._save())
        self._content.add_widget(save_btn)

        if not self.first_run:
            back_btn = action_button("← Back", bg_color=(0.2, 0.2, 0.3, 1),
                                     height=dp(44))
            back_btn.bind(on_release=lambda _: App.get_running_app().go_home())
            self._content.add_widget(back_btn)

        sv.add_widget(self._content)
        root.add_widget(sv)
        self.add_widget(root)

    # ------------------------------------------------------------------
    def _on_provider_change(self, spinner, display_name: str):
        self._current_provider = _PROVIDER_LABELS.get(display_name, "azure")
        self._desc_lbl.text = self._provider_description(self._current_provider)
        self._cred_card.clear_widgets()
        self._rebuild_cred_fields(self._current_provider)
        self._set_status("", SUBTEXT)

    # ------------------------------------------------------------------
    def _rebuild_cred_fields(self, provider: str):
        """Populate self._cred_card with the fields for *provider*."""
        s = self._settings
        self._fields.clear()

        def _add(key, label, hint, password=False):
            self._cred_card.add_widget(auto_label(text=label, font_size=dp(13), color=SUBTEXT))
            ti = _text_input(text=s.get(key, ""), hint=hint, password=password)
            self._cred_card.add_widget(ti)
            self._fields[key] = ti

        if provider == "azure":
            _add("azure_openai_endpoint",    "Endpoint URL",
                 "https://your-resource.openai.azure.com/")
            _add("azure_openai_api_key",     "API Key",
                 "Your Azure OpenAI API key", password=True)
            _add("azure_openai_deployment",  "Deployment Name",
                 "e.g. gpt-4o, gpt-4o-mini")
            _add("azure_openai_api_version", "API Version",
                 "2024-08-01-preview")

        elif provider == "openai":
            _add("openai_api_key", "API Key",
                 "sk-...", password=True)
            _add("openai_model",   "Model",
                 "gpt-4o-mini  |  gpt-4o  |  gpt-4-turbo")

        elif provider == "ollama":
            _add("ollama_base_url", "Ollama Base URL",
                 "http://localhost:11434")
            _add("ollama_model",    "Model Name",
                 "llama3.1  |  phi3  |  mistral  |  gemma2")

    # ------------------------------------------------------------------
    @staticmethod
    def _provider_description(provider: str) -> str:
        return {
            "azure":  "Azure OpenAI — managed cloud service, requires an Azure subscription.",
            "openai": "OpenAI — direct access to GPT-4o, GPT-4o-mini and others via api.openai.com.",
            "ollama": "Ollama — run open-source models locally (Llama, Phi, Mistral, Gemma…). "
                      "No internet required.",
        }.get(provider, "")

    # ------------------------------------------------------------------
    def _current_values(self) -> dict:
        values = dict(self._settings)          # keep unchanged provider fields
        values["ai_provider"] = self._current_provider
        for k, ti in self._fields.items():
            values[k] = ti.text.strip()
        return values

    def _set_status(self, msg: str, color=SUBTEXT):
        self._status_lbl.markup = True
        self._status_lbl.color = color
        self._status_lbl.text = emoji_markup(msg)

    # ------------------------------------------------------------------
    def _test_connection(self):
        self._set_status("Testing connection…", SUBTEXT)
        threading.Thread(target=self._do_test, daemon=True).start()

    def _do_test(self):
        values   = self._current_values()
        provider = values["ai_provider"]

        try:
            import httpx

            if provider == "ollama":
                # Hit the /api/tags endpoint — lists available models
                base = values.get("ollama_base_url", "").rstrip("/")
                if not base:
                    raise ValueError("Ollama Base URL is required.")
                resp = httpx.get(f"{base}/api/tags", timeout=8)
                if resp.status_code == 200:
                    models = [m["name"] for m in resp.json().get("models", [])]
                    snippet = ", ".join(models[:5]) or "none pulled yet"
                    Clock.schedule_once(lambda _: self._set_status(
                        f"✅  Ollama reachable. Models: {snippet}", SUCCESS))
                else:
                    Clock.schedule_once(lambda _: self._set_status(
                        f"⚠️  HTTP {resp.status_code} from Ollama.", WARNING))
                return

            # OpenAI or Azure — send a minimal chat completion
            if provider == "openai":
                url     = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {values.get('openai_api_key','')}",
                           "Content-Type": "application/json"}
                model   = values.get("openai_model", "gpt-4o-mini")
            else:  # azure
                endpoint   = values.get("azure_openai_endpoint", "").rstrip("/")
                deployment = values.get("azure_openai_deployment", "")
                api_ver    = values.get("azure_openai_api_version", "2024-08-01-preview")
                api_key    = values.get("azure_openai_api_key", "")
                if not (endpoint and api_key and deployment):
                    Clock.schedule_once(lambda _: self._set_status(
                        "❌  Fill in Endpoint, API Key and Deployment first.", DANGER))
                    return
                if endpoint.endswith("/v1"):
                    url     = f"{endpoint}/chat/completions"
                    headers = {"Authorization": f"Bearer {api_key}",
                               "Content-Type": "application/json"}
                else:
                    url     = (f"{endpoint}/openai/deployments/{deployment}"
                               f"/chat/completions?api-version={api_ver}")
                    headers = {"api-key": api_key, "Content-Type": "application/json"}
                model = deployment

            body = {"model": model,
                    "messages": [{"role": "user", "content": "ping"}],
                    "max_tokens": 1}
            resp = httpx.post(url, headers=headers, json=body, timeout=10)

            if resp.status_code in (200, 400):
                Clock.schedule_once(lambda _: self._set_status(
                    "✅  Connection successful!", SUCCESS))
            elif resp.status_code == 401:
                Clock.schedule_once(lambda _: self._set_status(
                    "❌  Unauthorized — check your API key.", DANGER))
            elif resp.status_code == 404:
                Clock.schedule_once(lambda _: self._set_status(
                    "❌  Not found — check endpoint / model name.", DANGER))
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
            self._set_status("⚠️  Required fields are missing.", WARNING)
            return

        save_settings(values)
        apply_settings(values)
        self._settings = values
        self._set_status("✅  Settings saved!", SUCCESS)

        if self.first_run:
            self.first_run = False
            Clock.schedule_once(lambda _: App.get_running_app().go_home(), 1.2)
