# ML Interview Prep — Mobile App 📱

A Kivy-based mobile version of the ML Interview Prep app that shares all core logic
(`config.py`, `data_manager.py`, `question_generator.py`, `scenario_questions.py`)
with the desktop app.

## Architecture

```
mobile/
├── main.py                  # Entry point; adds project root to sys.path
├── app.py                   # Kivy App class + ScreenManager + shared quiz state
├── buildozer.spec           # Android / iOS build configuration
├── requirements.txt         # Mobile-specific Python dependencies
├── README.md
└── screens/
    ├── styles.py            # Shared color constants and widget factories
    ├── home_screen.py       # Dashboard: stats, level progress, quiz launch
    ├── quiz_screen.py       # MCQ quiz: loads questions, steps through one by one
    ├── results_screen.py    # Score, points earned, level-up notification
    └── review_screen.py     # Full question-by-question answer breakdown
```

Shared logic lives in the **project root** (not inside `mobile/`) and is imported
via `sys.path` manipulation in `main.py`:

| File                    | Responsibility                        |
|-------------------------|---------------------------------------|
| `config.py`             | Topics, difficulty levels, API config |
| `data_manager.py`       | JSON persistence, stats, level-up     |
| `question_generator.py` | Azure OpenAI question generation      |
| `scenario_questions.py` | Hardcoded scenario/trick questions    |

## Prerequisites

1. **Python 3.10+**
2. **Kivy 2.3+** and dependencies
3. Azure OpenAI credentials (same `.env` as the desktop app)

## Development Setup (Desktop)

Run the mobile UI on your desktop to iterate quickly before building for device:

```bash
# From the project root
cd mobile
pip install -r requirements.txt

# Copy or symlink the root .env so credentials are found
cp ../.env .env   # Windows: copy ..\.env .env

python main.py
```

The window will open at 390×844 px (iPhone 14 Pro size) by default.
Set `MOBILE_DEV_MODE=0` to disable the fixed window size.

## Android Build

Uses [Buildozer](https://buildozer.readthedocs.io):

```bash
pip install buildozer
cd mobile
buildozer android debug          # first build (downloads NDK/SDK — ~20 min)
buildozer android debug deploy   # build + install on connected device
```

> **Note**: Buildozer runs on Linux/macOS. On Windows use WSL2 or a Linux VM.

## iOS Build

Uses [kivy-ios](https://github.com/kivy/kivy-ios) on macOS with Xcode installed:

```bash
pip install kivy-ios
toolchain build python3 kivy
toolchain create MLInterviewPrep .
open MLInterviewPrep-ios/MLInterviewPrep.xcodeproj
```

## Screens

| Screen     | Description                                                       |
|------------|-------------------------------------------------------------------|
| **Home**   | Level progress bar, accuracy/quiz/points stats, difficulty picker |
| **Quiz**   | Step-through MCQ with background API loading and progress bar     |
| **Results**| Score card, points earned, level-up banner, link to review        |
| **Review** | All questions with correct/wrong highlights and explanations      |

## Azure OpenAI Configuration

Set the same environment variables as the desktop app (or use a `.env` file in the
`mobile/` directory):

```
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_DEPLOYMENT=<your-deployment-name>
```
