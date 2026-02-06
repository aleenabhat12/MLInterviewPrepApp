# ML Interview Prep 🎯

A desktop application that uses AI to generate multiple-choice questions on Machine Learning concepts to help you prepare for ML interviews.

## Features

- **AI-Powered Question Generation**: Uses GitHub Models (GPT-4.1-mini) to generate relevant, challenging MCQ questions
- **Three Difficulty Levels**: Beginner, Intermediate, and Advanced
- **Comprehensive Topic Coverage**:
  - Statistics and Probability
  - Neural Networks (CNN, RNN)
  - Transformers and Attention Mechanisms
  - LLM Pre-training and Fine-tuning
  - Prompt Engineering
  - RAG (Retrieval-Augmented Generation)
  - Model Evaluation and Metrics
  - RLHF and Reinforcement Learning
  - Human-in-the-Loop (HITL)
  - And more!
- **Progress Tracking**: Track your scores, accuracy, and points across sessions
- **Level Progression**: Earn points to level up from Beginner → Intermediate → Advanced
- **Smart Recommendations**: Get suggestions on which topics to focus on based on your performance
- **Weak Area Focus**: Option to generate quizzes targeting your weak areas
- **Detailed Review**: See explanations for each question after completing a quiz

## Prerequisites

1. **Python 3.8+** installed on your system
2. **GitHub Personal Access Token (PAT)** with access to GitHub Models

## Installation

1. Clone or download this repository

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   The `--pre` flag may be needed for preview packages.

3. Set up your GitHub Token:
   
   **Windows (PowerShell):**
   ```powershell
   $env:GITHUB_TOKEN = "your_github_token_here"
   ```
   
   **Windows (Command Prompt):**
   ```cmd
   set GITHUB_TOKEN=your_github_token_here
   ```
   
   **Linux/macOS:**
   ```bash
   export GITHUB_TOKEN="your_github_token_here"
   ```

## Running the Application

```bash
python app.py
```

## How to Use

1. **Start a Quiz**: Select a difficulty level (Beginner, Intermediate, or Advanced) to start a quiz
2. **Answer Questions**: Select your answer for each multiple-choice question
3. **Review Results**: After completing the quiz, see your score and detailed explanations
4. **Track Progress**: Your progress is automatically saved and displayed on the home screen
5. **Focus on Weak Areas**: Use the "Focus on Weak Areas" button to get questions on topics you need to improve
6. **Level Up**: Earn points by answering questions correctly to advance to higher levels

## Scoring System

| Level | Points per Correct Answer | Points to Level Up |
|-------|---------------------------|-------------------|
| Beginner | 10 | 100 |
| Intermediate | 15 | 200 |
| Advanced | 25 | Max Level |

## Project Structure

```
MLInterviewPrep/
├── app.py              # Main application with GUI
├── config.py           # Configuration and constants
├── data_manager.py     # Data persistence and statistics
├── question_generator.py # LLM-based question generation
├── quiz_history.json   # Your saved progress (auto-generated)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Tips for Success

1. **Start with Beginner**: Even if you're experienced, starting with Beginner helps build confidence
2. **Focus on Weak Areas**: Use the weak area focus feature to improve where you need it most
3. **Review Explanations**: Always read the explanations after each quiz to learn from mistakes
4. **Practice Regularly**: Consistent practice is key to interview success
5. **Level Up Gradually**: Don't rush to Advanced - make sure you understand the fundamentals

## Troubleshooting

### "GITHUB_TOKEN environment variable not set"
Make sure you've set the GITHUB_TOKEN environment variable before running the app.

### Questions fail to generate
- Check your internet connection
- Verify your GitHub token is valid and has access to GitHub Models
- Try again - sometimes API calls can fail temporarily

### App crashes on startup
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Make sure you're using Python 3.8 or higher

## License

MIT License - Feel free to use and modify for your interview preparation!

---

Good luck with your ML interviews! 🚀
