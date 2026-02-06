"""Data manager for persisting quiz history and user progress."""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from config import ML_TOPICS, DIFFICULTY_LEVELS

DATA_FILE = "quiz_history.json"


def get_data_path() -> str:
    """Get the path to the data file."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILE)


def load_data() -> Dict:
    """Load user data from file."""
    data_path = get_data_path()
    if os.path.exists(data_path):
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return create_default_data()
    return create_default_data()


def save_data(data: Dict) -> None:
    """Save user data to file."""
    data_path = get_data_path()
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)


def create_default_data() -> Dict:
    """Create default data structure."""
    topic_stats = {}
    for topic in ML_TOPICS:
        topic_stats[topic] = {
            "total_questions": 0,
            "correct_answers": 0,
            "beginner": {"total": 0, "correct": 0},
            "intermediate": {"total": 0, "correct": 0},
            "advanced": {"total": 0, "correct": 0}
        }
    
    return {
        "current_level": "beginner",
        "total_points": 0,
        "level_points": 0,  # Points in current level
        "total_quizzes": 0,
        "total_questions": 0,
        "total_correct": 0,
        "topic_stats": topic_stats,
        "quiz_history": [],
        "created_at": datetime.now().isoformat(),
        "last_quiz_at": None
    }


def record_quiz_result(questions: List[Dict], answers: List[int], level: str) -> Dict:
    """Record the results of a quiz."""
    data = load_data()
    
    correct_count = 0
    topic_results = {}
    
    for i, question in enumerate(questions):
        topic = question.get("topic", "Unknown")
        is_correct = answers[i] == question.get("correct_answer", -1)
        
        if is_correct:
            correct_count += 1
        
        # Update topic stats
        if topic in data["topic_stats"]:
            data["topic_stats"][topic]["total_questions"] += 1
            data["topic_stats"][topic][level]["total"] += 1
            if is_correct:
                data["topic_stats"][topic]["correct_answers"] += 1
                data["topic_stats"][topic][level]["correct"] += 1
        
        # Track for this quiz
        if topic not in topic_results:
            topic_results[topic] = {"total": 0, "correct": 0}
        topic_results[topic]["total"] += 1
        if is_correct:
            topic_results[topic]["correct"] += 1
    
    # Calculate points earned
    points_per_correct = DIFFICULTY_LEVELS[level]["correct_answer_points"]
    points_earned = correct_count * points_per_correct
    
    # Update totals
    data["total_quizzes"] += 1
    data["total_questions"] += len(questions)
    data["total_correct"] += correct_count
    data["total_points"] += points_earned
    data["level_points"] += points_earned
    data["last_quiz_at"] = datetime.now().isoformat()
    
    # Check for level up
    level_up = False
    new_level = level
    points_to_next = DIFFICULTY_LEVELS[level]["points_to_level_up"]
    
    if points_to_next and data["level_points"] >= points_to_next:
        levels = list(DIFFICULTY_LEVELS.keys())
        current_idx = levels.index(level)
        if current_idx < len(levels) - 1:
            new_level = levels[current_idx + 1]
            data["current_level"] = new_level
            data["level_points"] = data["level_points"] - points_to_next
            level_up = True
    
    # Record quiz in history
    quiz_record = {
        "date": datetime.now().isoformat(),
        "level": level,
        "total_questions": len(questions),
        "correct_answers": correct_count,
        "points_earned": points_earned,
        "topics": list(topic_results.keys())
    }
    data["quiz_history"].append(quiz_record)
    
    # Keep only last 100 quizzes in history
    if len(data["quiz_history"]) > 100:
        data["quiz_history"] = data["quiz_history"][-100:]
    
    save_data(data)
    
    return {
        "correct_count": correct_count,
        "total_questions": len(questions),
        "points_earned": points_earned,
        "level_up": level_up,
        "new_level": new_level,
        "level_points": data["level_points"],
        "points_to_next": DIFFICULTY_LEVELS[new_level]["points_to_level_up"]
    }


def get_weak_topics(limit: int = 5) -> List[Dict]:
    """Get topics where user needs improvement, sorted by weakness."""
    data = load_data()
    topic_scores = []
    
    for topic, stats in data["topic_stats"].items():
        if stats["total_questions"] > 0:
            accuracy = stats["correct_answers"] / stats["total_questions"]
            topic_scores.append({
                "topic": topic,
                "accuracy": accuracy,
                "total_questions": stats["total_questions"],
                "correct_answers": stats["correct_answers"]
            })
    
    # Sort by accuracy (lowest first) then by total questions (most first for tie-breaker)
    topic_scores.sort(key=lambda x: (x["accuracy"], -x["total_questions"]))
    
    return topic_scores[:limit]


def get_strong_topics(limit: int = 5) -> List[Dict]:
    """Get topics where user performs well."""
    data = load_data()
    topic_scores = []
    
    for topic, stats in data["topic_stats"].items():
        if stats["total_questions"] >= 3:  # Need at least 3 questions to be considered strong
            accuracy = stats["correct_answers"] / stats["total_questions"]
            topic_scores.append({
                "topic": topic,
                "accuracy": accuracy,
                "total_questions": stats["total_questions"],
                "correct_answers": stats["correct_answers"]
            })
    
    # Sort by accuracy (highest first)
    topic_scores.sort(key=lambda x: (-x["accuracy"], -x["total_questions"]))
    
    return topic_scores[:limit]


def get_untested_topics() -> List[str]:
    """Get topics that haven't been tested yet."""
    data = load_data()
    untested = []
    
    for topic, stats in data["topic_stats"].items():
        if stats["total_questions"] == 0:
            untested.append(topic)
    
    return untested


def get_level_progress() -> Dict:
    """Get current level progress information."""
    data = load_data()
    current_level = data["current_level"]
    level_points = data["level_points"]
    points_to_next = DIFFICULTY_LEVELS[current_level]["points_to_level_up"]
    
    if points_to_next:
        progress_percent = min(100, (level_points / points_to_next) * 100)
        points_remaining = points_to_next - level_points
    else:
        progress_percent = 100
        points_remaining = 0
    
    return {
        "current_level": current_level,
        "level_name": DIFFICULTY_LEVELS[current_level]["name"],
        "level_points": level_points,
        "points_to_next": points_to_next,
        "progress_percent": progress_percent,
        "points_remaining": points_remaining,
        "total_points": data["total_points"],
        "is_max_level": points_to_next is None
    }


def get_overall_stats() -> Dict:
    """Get overall user statistics."""
    data = load_data()
    
    accuracy = 0
    if data["total_questions"] > 0:
        accuracy = (data["total_correct"] / data["total_questions"]) * 100
    
    return {
        "total_quizzes": data["total_quizzes"],
        "total_questions": data["total_questions"],
        "total_correct": data["total_correct"],
        "accuracy": accuracy,
        "total_points": data["total_points"],
        "current_level": data["current_level"],
        "last_quiz_at": data["last_quiz_at"]
    }


def reset_progress() -> None:
    """Reset all user progress."""
    data = create_default_data()
    save_data(data)
