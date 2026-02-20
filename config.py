"""Configuration for the ML Interview Prep application."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ML Topics for question generation
ML_TOPICS = [
    "Statistics and Probability",
    "Linear Algebra",
    "Neural Networks Fundamentals",
    "Convolutional Neural Networks (CNN)",
    "Recurrent Neural Networks (RNN)",
    "Transformers Architecture",
    "Attention Mechanisms",
    "BERT and GPT Models",
    "Retrieval-Augmented Generation (RAG)",
    "LLM Pre-training",
    "LLM Fine-tuning",
    "Prompt Engineering",
    "Few-shot and Zero-shot Learning",
    "Model Evaluation Metrics",
    "A/B Testing and Experimentation",
    "Human-in-the-Loop (HITL)",
    "Reinforcement Learning Basics",
    "Policy Gradient Methods",
    "RLHF (Reinforcement Learning from Human Feedback)",
    "Model Optimization and Quantization",
    "Embeddings and Vector Databases",
    "Loss Functions",
    "Regularization Techniques",
    "Gradient Descent Optimization",
    "Hyperparameter Tuning"
]

# Difficulty levels and their thresholds
DIFFICULTY_LEVELS = {
    "beginner": {
        "name": "Beginner",
        "color": "#28a745",
        "points_to_level_up": 100,
        "correct_answer_points": 10
    },
    "intermediate": {
        "name": "Intermediate", 
        "color": "#ffc107",
        "points_to_level_up": 200,
        "correct_answer_points": 15
    },
    "advanced": {
        "name": "Advanced",
        "color": "#dc3545",
        "points_to_level_up": None,  # Max level
        "correct_answer_points": 25
    }
}

# Number of questions per quiz
QUESTIONS_PER_QUIZ = 30

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
