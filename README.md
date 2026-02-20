# ML Interview Prep 🎯

A desktop application that uses AI to generate multiple-choice questions on Machine Learning concepts to help you prepare for ML interviews.

## Features

- **AI-Powered Question Generation**: Uses Azure OpenAI to generate relevant, challenging MCQ questions
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
2. **Azure OpenAI resource** with a deployed model (e.g. `gpt-4o`, `gpt-4`)

## Installation

1. Clone or download this repository

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Azure OpenAI credentials by copying the example env file and filling in your values:
   ```bash
   cp .env.example .env
   ```

   Then edit `.env`:
   ```
   AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
   AZURE_OPENAI_API_KEY=<your-api-key>
   AZURE_OPENAI_DEPLOYMENT=<your-deployment-name>
   AZURE_OPENAI_API_VERSION=2024-08-01-preview
   ```

   Alternatively, set the variables in your shell:

   **Windows (PowerShell):**
   ```powershell
   $env:AZURE_OPENAI_ENDPOINT = "https://<your-resource>.openai.azure.com/"
   $env:AZURE_OPENAI_API_KEY  = "<your-api-key>"
   $env:AZURE_OPENAI_DEPLOYMENT = "<your-deployment-name>"
   ```

   **Linux/macOS:**
   ```bash
   export AZURE_OPENAI_ENDPOINT="https://<your-resource>.openai.azure.com/"
   export AZURE_OPENAI_API_KEY="<your-api-key>"
   export AZURE_OPENAI_DEPLOYMENT="<your-deployment-name>"
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
├── scenario_questions.py # Built-in scenario/trick questions
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

### "Azure OpenAI credentials not configured"
Make sure `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, and `AZURE_OPENAI_DEPLOYMENT` are set — either in a `.env` file or as environment variables.

### Questions fail to generate
- Check your internet connection
- Verify your Azure OpenAI resource is active and the deployment name is correct
- Check that your API key has not expired
- Try again — sometimes API calls can fail temporarily

### App crashes on startup
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Make sure you're using Python 3.8 or higher

## License

MIT License - Feel free to use and modify for your interview preparation!

---

Good luck with your ML interviews! 🚀

