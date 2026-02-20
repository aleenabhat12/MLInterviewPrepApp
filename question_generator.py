"""Question generator using Azure OpenAI."""

import json
import random
from typing import List, Dict, Optional
import httpx

from config import (
    ML_TOPICS, QUESTIONS_PER_QUIZ,
    AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_VERSION
)
from scenario_questions import SCENARIO_FEW_SHOT_EXAMPLES


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
