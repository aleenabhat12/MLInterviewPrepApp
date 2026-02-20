"""Question generator using Azure OpenAI."""

import json
import random
from typing import List, Dict, Optional
import httpx

from config import (
    ML_TOPICS, QUESTIONS_PER_QUIZ,
    AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_VERSION
)


def _build_api_url() -> str:
    """Build the Azure OpenAI chat completions URL from the configured endpoint.

    Supports two endpoint styles:
    - OpenAI-compatible (/openai/v1): append /chat/completions directly.
    - Standard Azure OpenAI base URL: build the deployment-specific path.
    """
    base_url = AZURE_OPENAI_ENDPOINT.rstrip('/')
    if base_url.endswith('/v1'):
        return f"{base_url}/chat/completions"
    return (
        f"{base_url}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}"
        f"/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"
    )


def _strip_markdown_fences(text: str) -> str:
    """Strip markdown code fences (```...```) from a response string."""
    if not text.startswith("```"):
        return text
    lines = text.split("\n")
    json_lines = []
    in_block = False
    for line in lines:
        if line.startswith("```") and not in_block:
            in_block = True
            continue
        elif line.startswith("```") and in_block:
            break
        elif in_block:
            json_lines.append(line)
    return "\n".join(json_lines)


def _call_openai_api(messages: List[Dict], max_tokens: int, temperature: float) -> str:
    """Call Azure OpenAI chat completions and return the response text.

    Returns an empty string if the response has no content.
    Raises ValueError on HTTP errors, re-raises other exceptions.
    """
    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
        raise ValueError(
            "Azure OpenAI credentials not configured. "
            "Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in .env file."
        )
    if not AZURE_OPENAI_DEPLOYMENT:
        raise ValueError(
            "Azure OpenAI deployment name not configured. "
            "Please set AZURE_OPENAI_DEPLOYMENT in .env file."
        )

    api_url = _build_api_url()
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_API_KEY,
    }
    payload = {
        "model": AZURE_OPENAI_DEPLOYMENT,
        "messages": messages,
        "max_completion_tokens": max_tokens,
        "temperature": temperature,
    }

    print(f"Calling Azure OpenAI API: {api_url}")
    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise ValueError(f"API error: {e.response.status_code} - {e.response.text[:200]}") from e

    result = response.json()
    if "choices" in result and len(result["choices"]) > 0:
        return result["choices"][0].get("message", {}).get("content", "")

    print(f"Empty response from API: {result}")
    return ""


def generate_questions(
    level: str,
    topics: Optional[List[str]] = None,
    num_questions: int = QUESTIONS_PER_QUIZ,
    focus_weak_areas: bool = False,
    weak_topics: Optional[List[str]] = None
) -> List[Dict]:
    """
    Generate multiple choice questions using Azure OpenAI.
    
    Args:
        level: Difficulty level (beginner, intermediate, advanced)
        topics: Specific topics to focus on (if None, random selection)
        num_questions: Number of questions to generate
        focus_weak_areas: Whether to focus on weak areas
        weak_topics: List of weak topics to prioritize
    
    Returns:
        List of question dictionaries
    """
    # Select topics for questions - distribute across all topics
    if topics:
        selected_topics = topics
    elif focus_weak_areas and weak_topics:
        # Prioritize weak topics but include variety
        selected_topics = []
        weak_count = min(len(weak_topics), num_questions // 2)
        selected_topics.extend(weak_topics[:weak_count])
        
        remaining = num_questions - len(selected_topics)
        other_topics = [t for t in ML_TOPICS if t not in selected_topics]
        if remaining > 0 and other_topics:
            selected_topics.extend(random.sample(other_topics, min(remaining, len(other_topics))))
    else:
        # Distribute questions across topics
        selected_topics = []
        topics_cycle = ML_TOPICS.copy()
        random.shuffle(topics_cycle)
        while len(selected_topics) < num_questions:
            selected_topics.extend(topics_cycle)
        selected_topics = selected_topics[:num_questions]
    
    # Shuffle final selection
    random.shuffle(selected_topics)
    
    # Create the prompt
    level_descriptions = {
        "beginner": "basic conceptual understanding, definitions, and fundamental principles. Questions should test foundational knowledge.",
        "intermediate": "practical applications, trade-offs, implementation details, and deeper understanding of mechanisms. Questions should require applying concepts.",
        "advanced": "complex scenarios, edge cases, mathematical foundations, optimization strategies, and expert-level insights. Questions should challenge deep expertise."
    }
    
    # Group topics for the prompt
    topic_counts = {}
    for t in selected_topics:
        topic_counts[t] = topic_counts.get(t, 0) + 1
    
    topics_str = ", ".join([f"{t} ({c} questions)" for t, c in topic_counts.items()])
    
    prompt = f"""Generate exactly {num_questions} multiple choice questions for a Machine Learning interview preparation quiz.

Difficulty Level: {level.upper()}
Focus: {level_descriptions[level]}

Topics to cover with question distribution: {topics_str}

Requirements:
1. Each question must have exactly 4 answer options (A, B, C, D)
2. Only ONE option should be correct
3. Wrong answers should be plausible but clearly incorrect to someone who knows the material
4. Include a brief explanation for why the correct answer is right
5. Questions should be practical and reflect real ML interview questions
6. Vary the question types: conceptual, computational, scenario-based, comparison

Return ONLY valid JSON in this exact format (no markdown, no code blocks, just pure JSON):
{{
    "questions": [
        {{
            "topic": "Topic Name",
            "question": "The question text?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Explanation of why this is correct."
        }}
    ]
}}

Generate all {num_questions} questions now:"""

    messages = [
        {
            "role": "system",
            "content": "You are an expert ML engineer and educator creating interview preparation questions. Generate accurate, educational, and appropriately challenging multiple choice questions. Always respond with valid JSON only, no markdown formatting."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    try:
        response_text = _call_openai_api(messages, max_tokens=16000, temperature=0.7)
        if not response_text:
            return []

        response_text = _strip_markdown_fences(response_text.strip())
        data = json.loads(response_text)
        questions = data.get("questions", [])

        validated_questions = []
        for q in questions:
            if all(key in q for key in ["topic", "question", "options", "correct_answer", "explanation"]):
                if len(q["options"]) == 4 and 0 <= q["correct_answer"] <= 3:
                    validated_questions.append(q)

        print(f"Generated {len(validated_questions)} valid questions out of {len(questions)} total")
        return validated_questions

    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response: {e}")
        print(f"Response text: {response_text[:500] if 'response_text' in locals() else 'N/A'}")
        return []
    except Exception as e:
        print(f"Error generating questions: {e}")
        raise


def generate_single_question(topic: str, level: str) -> Optional[Dict]:
    """Generate a single question on a specific topic."""
    questions = generate_questions(level=level, topics=[topic], num_questions=1)
    return questions[0] if questions else None


# Few-shot examples for scenario-based questions
SCENARIO_FEW_SHOT_EXAMPLES = [
    {
        "topic": "Tokenization / Domain Adaptation",
        "category": "LLM & NLP",
        "scenario": "A medical-domain startup is building an LLM assistant for radiology reports. Their dataset contains heavy use of complex, compound medical terms (e.g., 'hyperdenseextra-axialhemorrhage'). Consider the tradeoffs for: vocabulary fragmentation, model perplexity, downstream fine-tuning stability, and rare word generalization.",
        "question": "Which tokenization strategy should they choose?",
        "options": [
            "Train a tokenizer from scratch on their domain corpus",
            "Use the tokenizer from a general-purpose LLM (e.g., GPT-style)",
            "Use a hybrid approach (retain base tokenizer + add domain-specific merges)",
            "Use character-level tokenization for maximum flexibility"
        ],
        "correct_answer": 2,
        "explanation": "The hybrid approach (C) is optimal because: it reduces vocabulary fragmentation for medical terms while retaining pretrained knowledge, balances model perplexity across domain and general text, maintains fine-tuning stability by keeping most embeddings pretrained, and benefits from transfer learning for rare word generalization. Training from scratch loses pretrained knowledge, using general tokenizer causes severe fragmentation, and character-level is computationally expensive."
    },
    {
        "topic": "Overfitting / Bias-Variance",
        "category": "Model Evaluation",
        "scenario": "You train a binary classifier with: Training accuracy: 100%, Validation accuracy: fluctuates between 45-60%, ROC curve on held-out set is almost diagonal, SHAP values show unstable feature importance between runs.",
        "question": "What is happening and what minimal ONE change would you apply first?",
        "options": [
            "Underfitting - increase model complexity by adding more layers",
            "Severe overfitting - add regularization (L2/Dropout)",
            "Data leakage - rebuild the train/validation split",
            "Label noise - apply label smoothing"
        ],
        "correct_answer": 1,
        "explanation": "This is severe overfitting: 100% training / ~50% validation = memorization, diagonal ROC = random guessing performance, fluctuating SHAP = model learns different spurious patterns each run. Regularization (L2/Dropout) is the best first fix as it directly penalizes complexity and prevents memorization. Adding layers would worsen overfitting."
    },
    {
        "topic": "Distribution Shift / MLOps",
        "category": "MLOps",
        "scenario": "A segmentation model works perfectly on validation but fails on real-world data showing: lower resolution, motion blur, different lighting, new background patterns.",
        "question": "What is the FASTEST mitigation without retraining?",
        "options": [
            "Collect more training data from the real-world distribution",
            "Test-Time Augmentation (TTA) - average predictions over augmented versions of input",
            "Fine-tune the model on a small set of real-world examples",
            "Switch to a larger model architecture"
        ],
        "correct_answer": 1,
        "explanation": "Test-Time Augmentation (TTA) is the fastest fix without retraining: apply multiple augmentations to each test image (flip, rotate, scale), run inference on all versions, average predictions. This helps because some augmentations may match training distribution better, and averaging reduces prediction variance. No model changes or retraining needed."
    },
    {
        "topic": "Imbalanced Data Evaluation",
        "category": "Model Evaluation",
        "scenario": "Dataset: 0.5% fraud, 99.5% legitimate. A candidate reports: 'Model accuracy = 99.4%, so performance is excellent.' Additional evaluation shows: AUROC = 0.62, AUPRC = 0.04, FPR at threshold = 18%.",
        "question": "Which single metric BEST captures real-world performance for this problem?",
        "options": [
            "Accuracy - it gives the overall correctness",
            "AUROC - it measures discrimination ability",
            "AUPRC - it focuses on minority class performance",
            "F1 Score at default 0.5 threshold"
        ],
        "correct_answer": 2,
        "explanation": "AUPRC is best for imbalanced data because: it focuses on the minority class (fraud), is not inflated by true negatives, and directly measures what matters (finding fraud). The 99.4% accuracy is meaningless - a model predicting 'always legitimate' achieves 99.5% accuracy! AUROC can be misleadingly high with class imbalance."
    },
    {
        "topic": "Loss Landscape / Optimization",
        "category": "Training & Optimization",
        "scenario": "Your model trains normally for 10 epochs, then suddenly the loss spikes and remains unstable. You check: gradient norms → exploding, weight norms → growing, learning rate scheduler → constant LR, batch size → small (8).",
        "question": "How would you patch this without retraining from scratch?",
        "options": [
            "Delete the model and redesign the architecture",
            "Load checkpoint from epoch 8-9, add gradient clipping, reduce learning rate",
            "Increase batch size to 512 and continue from current unstable state",
            "Switch optimizer from Adam to SGD with momentum"
        ],
        "correct_answer": 1,
        "explanation": "Best patch: Load checkpoint from epoch 8-9 (last stable state), add gradient clipping (e.g., max_norm=1.0), reduce learning rate by 10x. This works because: checkpoint restores stable weights, gradient clipping prevents explosion, lower LR reduces overshoot risk. Continuing from unstable state won't recover."
    }
]


SCENARIO_CATEGORIES = [
    "LLM & NLP",
    "Classical ML", 
    "Neural Networks",
    "Model Evaluation",
    "MLOps",
    "Deep Learning",
    "Training & Optimization",
    "Data Engineering",
    "Feature Engineering",
    "Deployment & Production"
]


def generate_scenario_questions(
    category: Optional[str] = None,
    num_questions: int = 5
) -> List[Dict]:
    """
    Generate scenario-based questions using LLM with few-shot examples.
    
    Args:
        category: Specific category to focus on (if None, mix of categories)
        num_questions: Number of questions to generate
    
    Returns:
        List of scenario question dictionaries
    """
    # Build few-shot examples string
    examples_str = ""
    for i, ex in enumerate(SCENARIO_FEW_SHOT_EXAMPLES[:3], 1):  # Use 3 examples
        examples_str += f"""
Example {i}:
{{
    "topic": "{ex['topic']}",
    "category": "{ex['category']}",
    "scenario": "{ex['scenario']}",
    "question": "{ex['question']}",
    "options": {json.dumps(ex['options'])},
    "correct_answer": {ex['correct_answer']},
    "explanation": "{ex['explanation']}"
}}
"""
    
    # Determine categories to use
    if category:
        categories_str = category
    else:
        selected_cats = random.sample(SCENARIO_CATEGORIES, min(5, len(SCENARIO_CATEGORIES)))
        categories_str = ", ".join(selected_cats)
    
    prompt = f"""Generate exactly {num_questions} scenario-based multiple choice questions for advanced ML interview preparation.

These are "trick questions" or "case study" questions that test deep understanding, not just definitions.

Categories to cover: {categories_str}

Requirements:
1. Each question must present a REALISTIC SCENARIO (2-4 sentences describing a situation, problem, or observation)
2. The question should ask about diagnosis, best approach, trade-offs, or failure modes
3. Exactly 4 answer options - one correct, three plausible but wrong
4. Include a detailed explanation (2-4 sentences) explaining WHY the correct answer is right and why others are wrong
5. These should be questions that trip up candidates who only have surface-level knowledge
6. Focus on practical ML engineering scenarios: debugging, optimization, architecture decisions, evaluation pitfalls

Here are examples of the format and difficulty level expected:
{examples_str}

Return ONLY valid JSON in this exact format (no markdown, no code blocks, just pure JSON):
{{
    "questions": [
        {{
            "topic": "Short Topic Name",
            "category": "Category Name",
            "scenario": "A detailed scenario describing the situation...",
            "question": "The specific question to answer?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Detailed explanation of why this is correct and others are wrong."
        }}
    ]
}}

Generate {num_questions} unique, challenging scenario questions now:"""

    messages = [
        {
            "role": "system",
            "content": """You are a senior ML engineer and interviewer at a top tech company. 
You create challenging scenario-based interview questions that test deep understanding of ML concepts.
Your questions should expose candidates who only have surface-level knowledge.
Focus on real-world debugging, optimization decisions, and common pitfalls.
Always respond with valid JSON only, no markdown formatting."""
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    try:
        response_text = _call_openai_api(messages, max_tokens=8000, temperature=0.8)
        if not response_text:
            return []

        response_text = _strip_markdown_fences(response_text.strip())
        data = json.loads(response_text)
        questions = data.get("questions", [])

        validated_questions = []
        required_keys = ["topic", "category", "scenario", "question", "options", "correct_answer", "explanation"]
        for q in questions:
            if all(key in q for key in required_keys):
                if len(q["options"]) == 4 and 0 <= q["correct_answer"] <= 3:
                    validated_questions.append(q)

        print(f"Generated {len(validated_questions)} valid scenario questions out of {len(questions)} total")
        return validated_questions

    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response: {e}")
        print(f"Response text: {response_text[:500] if 'response_text' in locals() else 'N/A'}")
        return []
    except Exception as e:
        print(f"Error generating scenario questions: {e}")
        raise


def get_scenario_categories() -> List[str]:
    """Return available scenario categories."""
    return SCENARIO_CATEGORIES.copy()
    level: str,
    topics: Optional[List[str]] = None,
    num_questions: int = QUESTIONS_PER_QUIZ,
    focus_weak_areas: bool = False,
    weak_topics: Optional[List[str]] = None
) -> List[Dict]:
    """
    Generate multiple choice questions using Azure OpenAI.
    
    Args:
        level: Difficulty level (beginner, intermediate, advanced)
        topics: Specific topics to focus on (if None, random selection)
        num_questions: Number of questions to generate
        focus_weak_areas: Whether to focus on weak areas
        weak_topics: List of weak topics to prioritize
    
    Returns:
        List of question dictionaries
    """
    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
        raise ValueError(
            "Azure OpenAI credentials not configured. "
            "Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in .env file."
        )
    
    # Select topics for questions - distribute across all topics
    if topics:
        selected_topics = topics
    elif focus_weak_areas and weak_topics:
        # Prioritize weak topics but include variety
        selected_topics = []
        weak_count = min(len(weak_topics), num_questions // 2)
        selected_topics.extend(weak_topics[:weak_count])
        
        remaining = num_questions - len(selected_topics)
        other_topics = [t for t in ML_TOPICS if t not in selected_topics]
        if remaining > 0 and other_topics:
            selected_topics.extend(random.sample(other_topics, min(remaining, len(other_topics))))
    else:
        # Distribute questions across topics
        selected_topics = []
        topics_cycle = ML_TOPICS.copy()
        random.shuffle(topics_cycle)
        while len(selected_topics) < num_questions:
            selected_topics.extend(topics_cycle)
        selected_topics = selected_topics[:num_questions]
    
    # Shuffle final selection
    random.shuffle(selected_topics)
    
    # Create the prompt
    level_descriptions = {
        "beginner": "basic conceptual understanding, definitions, and fundamental principles. Questions should test foundational knowledge.",
        "intermediate": "practical applications, trade-offs, implementation details, and deeper understanding of mechanisms. Questions should require applying concepts.",
        "advanced": "complex scenarios, edge cases, mathematical foundations, optimization strategies, and expert-level insights. Questions should challenge deep expertise."
    }
    
    # Group topics for the prompt
    topic_counts = {}
    for t in selected_topics:
        topic_counts[t] = topic_counts.get(t, 0) + 1
    
    topics_str = ", ".join([f"{t} ({c} questions)" for t, c in topic_counts.items()])
    
    prompt = f"""Generate exactly {num_questions} multiple choice questions for a Machine Learning interview preparation quiz.

Difficulty Level: {level.upper()}
Focus: {level_descriptions[level]}

Topics to cover with question distribution: {topics_str}

Requirements:
1. Each question must have exactly 4 answer options (A, B, C, D)
2. Only ONE option should be correct
3. Wrong answers should be plausible but clearly incorrect to someone who knows the material
4. Include a brief explanation for why the correct answer is right
5. Questions should be practical and reflect real ML interview questions
6. Vary the question types: conceptual, computational, scenario-based, comparison

Return ONLY valid JSON in this exact format (no markdown, no code blocks, just pure JSON):
{{
    "questions": [
        {{
            "topic": "Topic Name",
            "question": "The question text?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Explanation of why this is correct."
        }}
    ]
}}

Generate all {num_questions} questions now:"""

    try:
        # Build the API URL for Azure OpenAI
        # The endpoint already has /openai/v1/ so we just add chat/completions
        base_url = AZURE_OPENAI_ENDPOINT.rstrip('/')
        if base_url.endswith('/v1'):
            api_url = f"{base_url}/chat/completions"
        else:
            api_url = f"{base_url}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"
        
        headers = {
            "Content-Type": "application/json",
            "api-key": AZURE_OPENAI_API_KEY,
        }
        
        payload = {
            "model": AZURE_OPENAI_DEPLOYMENT,
            "max_completion_tokens": 16000,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert ML engineer and educator creating interview preparation questions. Generate accurate, educational, and appropriately challenging multiple choice questions. Always respond with valid JSON only, no markdown formatting."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        print(f"Calling API: {api_url}")
        
        # Make the API call
        with httpx.Client(timeout=120.0) as client:
            response = client.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
        
        result = response.json()
        
        # Extract text from OpenAI response
        response_text = ""
        if "choices" in result and len(result["choices"]) > 0:
            response_text = result["choices"][0].get("message", {}).get("content", "")
        
        if not response_text:
            print(f"Empty response from API: {result}")
            return []
        
        # Clean up response - remove any markdown code blocks
        response_text = response_text.strip()
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            json_lines = []
            in_json = False
            for line in lines:
                if line.startswith("```") and not in_json:
                    in_json = True
                    continue
                elif line.startswith("```") and in_json:
                    break
                elif in_json:
                    json_lines.append(line)
            response_text = "\n".join(json_lines)
        
        # Parse JSON
        data = json.loads(response_text)
        questions = data.get("questions", [])
        
        # Validate questions
        validated_questions = []
        for q in questions:
            if all(key in q for key in ["topic", "question", "options", "correct_answer", "explanation"]):
                if len(q["options"]) == 4 and 0 <= q["correct_answer"] <= 3:
                    validated_questions.append(q)
        
        print(f"Generated {len(validated_questions)} valid questions out of {len(questions)} total")
        return validated_questions
        
    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response: {e}")
        print(f"Response text: {response_text[:500] if 'response_text' in dir() else 'N/A'}")
        return []
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code} - {e.response.text}")
        raise ValueError(f"API error: {e.response.status_code} - {e.response.text[:200]}")
    except Exception as e:
        print(f"Error generating questions: {e}")
        raise


def generate_single_question(topic: str, level: str) -> Optional[Dict]:
    """Generate a single question on a specific topic."""
    questions = generate_questions(level=level, topics=[topic], num_questions=1)
    return questions[0] if questions else None


# Few-shot examples for scenario-based questions
SCENARIO_FEW_SHOT_EXAMPLES = [
    {
        "topic": "Tokenization / Domain Adaptation",
        "category": "LLM & NLP",
        "scenario": "A medical-domain startup is building an LLM assistant for radiology reports. Their dataset contains heavy use of complex, compound medical terms (e.g., 'hyperdenseextra-axialhemorrhage'). Consider the tradeoffs for: vocabulary fragmentation, model perplexity, downstream fine-tuning stability, and rare word generalization.",
        "question": "Which tokenization strategy should they choose?",
        "options": [
            "Train a tokenizer from scratch on their domain corpus",
            "Use the tokenizer from a general-purpose LLM (e.g., GPT-style)",
            "Use a hybrid approach (retain base tokenizer + add domain-specific merges)",
            "Use character-level tokenization for maximum flexibility"
        ],
        "correct_answer": 2,
        "explanation": "The hybrid approach (C) is optimal because: it reduces vocabulary fragmentation for medical terms while retaining pretrained knowledge, balances model perplexity across domain and general text, maintains fine-tuning stability by keeping most embeddings pretrained, and benefits from transfer learning for rare word generalization. Training from scratch loses pretrained knowledge, using general tokenizer causes severe fragmentation, and character-level is computationally expensive."
    },
    {
        "topic": "Overfitting / Bias-Variance",
        "category": "Model Evaluation",
        "scenario": "You train a binary classifier with: Training accuracy: 100%, Validation accuracy: fluctuates between 45-60%, ROC curve on held-out set is almost diagonal, SHAP values show unstable feature importance between runs.",
        "question": "What is happening and what minimal ONE change would you apply first?",
        "options": [
            "Underfitting - increase model complexity by adding more layers",
            "Severe overfitting - add regularization (L2/Dropout)",
            "Data leakage - rebuild the train/validation split",
            "Label noise - apply label smoothing"
        ],
        "correct_answer": 1,
        "explanation": "This is severe overfitting: 100% training / ~50% validation = memorization, diagonal ROC = random guessing performance, fluctuating SHAP = model learns different spurious patterns each run. Regularization (L2/Dropout) is the best first fix as it directly penalizes complexity and prevents memorization. Adding layers would worsen overfitting."
    },
    {
        "topic": "Distribution Shift / MLOps",
        "category": "MLOps",
        "scenario": "A segmentation model works perfectly on validation but fails on real-world data showing: lower resolution, motion blur, different lighting, new background patterns.",
        "question": "What is the FASTEST mitigation without retraining?",
        "options": [
            "Collect more training data from the real-world distribution",
            "Test-Time Augmentation (TTA) - average predictions over augmented versions of input",
            "Fine-tune the model on a small set of real-world examples",
            "Switch to a larger model architecture"
        ],
        "correct_answer": 1,
        "explanation": "Test-Time Augmentation (TTA) is the fastest fix without retraining: apply multiple augmentations to each test image (flip, rotate, scale), run inference on all versions, average predictions. This helps because some augmentations may match training distribution better, and averaging reduces prediction variance. No model changes or retraining needed."
    },
    {
        "topic": "Imbalanced Data Evaluation",
        "category": "Model Evaluation",
        "scenario": "Dataset: 0.5% fraud, 99.5% legitimate. A candidate reports: 'Model accuracy = 99.4%, so performance is excellent.' Additional evaluation shows: AUROC = 0.62, AUPRC = 0.04, FPR at threshold = 18%.",
        "question": "Which single metric BEST captures real-world performance for this problem?",
        "options": [
            "Accuracy - it gives the overall correctness",
            "AUROC - it measures discrimination ability",
            "AUPRC - it focuses on minority class performance",
            "F1 Score at default 0.5 threshold"
        ],
        "correct_answer": 2,
        "explanation": "AUPRC is best for imbalanced data because: it focuses on the minority class (fraud), is not inflated by true negatives, and directly measures what matters (finding fraud). The 99.4% accuracy is meaningless - a model predicting 'always legitimate' achieves 99.5% accuracy! AUROC can be misleadingly high with class imbalance."
    },
    {
        "topic": "Loss Landscape / Optimization",
        "category": "Training & Optimization",
        "scenario": "Your model trains normally for 10 epochs, then suddenly the loss spikes and remains unstable. You check: gradient norms → exploding, weight norms → growing, learning rate scheduler → constant LR, batch size → small (8).",
        "question": "How would you patch this without retraining from scratch?",
        "options": [
            "Delete the model and redesign the architecture",
            "Load checkpoint from epoch 8-9, add gradient clipping, reduce learning rate",
            "Increase batch size to 512 and continue from current unstable state",
            "Switch optimizer from Adam to SGD with momentum"
        ],
        "correct_answer": 1,
        "explanation": "Best patch: Load checkpoint from epoch 8-9 (last stable state), add gradient clipping (e.g., max_norm=1.0), reduce learning rate by 10x. This works because: checkpoint restores stable weights, gradient clipping prevents explosion, lower LR reduces overshoot risk. Continuing from unstable state won't recover."
    }
]


SCENARIO_CATEGORIES = [
    "LLM & NLP",
    "Classical ML", 
    "Neural Networks",
    "Model Evaluation",
    "MLOps",
    "Deep Learning",
    "Training & Optimization",
    "Data Engineering",
    "Feature Engineering",
    "Deployment & Production"
]


def generate_scenario_questions(
    category: Optional[str] = None,
    num_questions: int = 5
) -> List[Dict]:
    """
    Generate scenario-based questions using LLM with few-shot examples.
    
    Args:
        category: Specific category to focus on (if None, mix of categories)
        num_questions: Number of questions to generate
    
    Returns:
        List of scenario question dictionaries
    """
    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
        raise ValueError(
            "Azure OpenAI credentials not configured. "
            "Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in .env file."
        )
    
    # Build few-shot examples string
    examples_str = ""
    for i, ex in enumerate(SCENARIO_FEW_SHOT_EXAMPLES[:3], 1):  # Use 3 examples
        examples_str += f"""
Example {i}:
{{
    "topic": "{ex['topic']}",
    "category": "{ex['category']}",
    "scenario": "{ex['scenario']}",
    "question": "{ex['question']}",
    "options": {json.dumps(ex['options'])},
    "correct_answer": {ex['correct_answer']},
    "explanation": "{ex['explanation']}"
}}
"""
    
    # Determine categories to use
    if category:
        categories_str = category
    else:
        selected_cats = random.sample(SCENARIO_CATEGORIES, min(5, len(SCENARIO_CATEGORIES)))
        categories_str = ", ".join(selected_cats)
    
    prompt = f"""Generate exactly {num_questions} scenario-based multiple choice questions for advanced ML interview preparation.

These are "trick questions" or "case study" questions that test deep understanding, not just definitions.

Categories to cover: {categories_str}

Requirements:
1. Each question must present a REALISTIC SCENARIO (2-4 sentences describing a situation, problem, or observation)
2. The question should ask about diagnosis, best approach, trade-offs, or failure modes
3. Exactly 4 answer options - one correct, three plausible but wrong
4. Include a detailed explanation (2-4 sentences) explaining WHY the correct answer is right and why others are wrong
5. These should be questions that trip up candidates who only have surface-level knowledge
6. Focus on practical ML engineering scenarios: debugging, optimization, architecture decisions, evaluation pitfalls

Here are examples of the format and difficulty level expected:
{examples_str}

Return ONLY valid JSON in this exact format (no markdown, no code blocks, just pure JSON):
{{
    "questions": [
        {{
            "topic": "Short Topic Name",
            "category": "Category Name",
            "scenario": "A detailed scenario describing the situation...",
            "question": "The specific question to answer?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Detailed explanation of why this is correct and others are wrong."
        }}
    ]
}}

Generate {num_questions} unique, challenging scenario questions now:"""

    try:
        # Build the API URL
        base_url = AZURE_OPENAI_ENDPOINT.rstrip('/')
        if base_url.endswith('/v1'):
            api_url = f"{base_url}/chat/completions"
        else:
            api_url = f"{base_url}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"
        
        headers = {
            "Content-Type": "application/json",
            "api-key": AZURE_OPENAI_API_KEY,
        }
        
        payload = {
            "model": AZURE_OPENAI_DEPLOYMENT,
            "max_completion_tokens": 8000,
            "temperature": 0.8,  # Slightly higher for more creative scenarios
            "messages": [
                {
                    "role": "system",
                    "content": """You are a senior ML engineer and interviewer at a top tech company. 
You create challenging scenario-based interview questions that test deep understanding of ML concepts.
Your questions should expose candidates who only have surface-level knowledge.
Focus on real-world debugging, optimization decisions, and common pitfalls.
Always respond with valid JSON only, no markdown formatting."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        print(f"Generating scenario questions via API: {api_url}")
        
        # Make the API call
        with httpx.Client(timeout=120.0) as client:
            response = client.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
        
        result = response.json()
        
        # Extract text from response
        response_text = ""
        if "choices" in result and len(result["choices"]) > 0:
            response_text = result["choices"][0].get("message", {}).get("content", "")
        
        if not response_text:
            print(f"Empty response from API: {result}")
            return []
        
        # Clean up response - remove any markdown code blocks
        response_text = response_text.strip()
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            json_lines = []
            in_json = False
            for line in lines:
                if line.startswith("```") and not in_json:
                    in_json = True
                    continue
                elif line.startswith("```") and in_json:
                    break
                elif in_json:
                    json_lines.append(line)
            response_text = "\n".join(json_lines)
        
        # Parse JSON
        data = json.loads(response_text)
        questions = data.get("questions", [])
        
        # Validate questions
        validated_questions = []
        required_keys = ["topic", "category", "scenario", "question", "options", "correct_answer", "explanation"]
        for q in questions:
            if all(key in q for key in required_keys):
                if len(q["options"]) == 4 and 0 <= q["correct_answer"] <= 3:
                    validated_questions.append(q)
        
        print(f"Generated {len(validated_questions)} valid scenario questions out of {len(questions)} total")
        return validated_questions
        
    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response: {e}")
        print(f"Response text: {response_text[:500] if 'response_text' in dir() else 'N/A'}")
        return []
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code} - {e.response.text}")
        raise ValueError(f"API error: {e.response.status_code} - {e.response.text[:200]}")
    except Exception as e:
        print(f"Error generating scenario questions: {e}")
        raise


def get_scenario_categories() -> List[str]:
    """Return available scenario categories."""
    return SCENARIO_CATEGORIES.copy()