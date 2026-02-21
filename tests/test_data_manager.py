"""Unit tests for data_manager.py."""

import json
import os
import tempfile
import pytest
from unittest.mock import patch

# Patch DATA_FILE path to use a temp file so tests never touch the real quiz_history.json
import data_manager


@pytest.fixture(autouse=True)
def tmp_data_file(tmp_path):
    """Redirect data_manager to a fresh temp file for every test."""
    tmp_file = str(tmp_path / "quiz_history.json")
    with patch.object(data_manager, "get_data_path", return_value=tmp_file):
        yield tmp_file


# ---------------------------------------------------------------------------
# create_default_data
# ---------------------------------------------------------------------------

class TestCreateDefaultData:
    def test_structure_keys(self):
        data = data_manager.create_default_data()
        expected = {
            "current_level", "total_points", "level_points", "total_quizzes",
            "total_questions", "total_correct", "topic_stats", "quiz_history",
            "created_at", "last_quiz_at",
        }
        assert expected.issubset(data.keys())

    def test_default_level_is_beginner(self):
        data = data_manager.create_default_data()
        assert data["current_level"] == "beginner"

    def test_all_points_zero(self):
        data = data_manager.create_default_data()
        assert data["total_points"] == 0
        assert data["level_points"] == 0
        assert data["total_quizzes"] == 0

    def test_topic_stats_populated(self):
        from config import ML_TOPICS
        data = data_manager.create_default_data()
        for topic in ML_TOPICS:
            assert topic in data["topic_stats"]
            assert data["topic_stats"][topic]["total_questions"] == 0

    def test_quiz_history_empty(self):
        data = data_manager.create_default_data()
        assert data["quiz_history"] == []


# ---------------------------------------------------------------------------
# load_data / save_data
# ---------------------------------------------------------------------------

class TestLoadSaveData:
    def test_load_returns_default_when_no_file(self, tmp_data_file):
        assert not os.path.exists(tmp_data_file)
        data = data_manager.load_data()
        assert data["current_level"] == "beginner"

    def test_round_trip(self, tmp_data_file):
        original = data_manager.create_default_data()
        original["total_points"] = 42
        data_manager.save_data(original)
        loaded = data_manager.load_data()
        assert loaded["total_points"] == 42

    def test_load_returns_default_on_corrupt_file(self, tmp_data_file):
        with open(tmp_data_file, "w") as f:
            f.write("not valid json{{")
        data = data_manager.load_data()
        assert data["current_level"] == "beginner"

    def test_load_trims_history_to_100(self, tmp_data_file):
        data = data_manager.create_default_data()
        data["quiz_history"] = [{"date": str(i)} for i in range(150)]
        data_manager.save_data(data)
        loaded = data_manager.load_data()
        assert len(loaded["quiz_history"]) == 100
        # Should keep the most recent 100
        assert loaded["quiz_history"][0]["date"] == "50"


# ---------------------------------------------------------------------------
# record_quiz_result
# ---------------------------------------------------------------------------

def _make_questions(n, topic="Neural Networks Fundamentals"):
    """Return n minimal question dicts all answering correctly at index 0."""
    return [
        {"topic": topic, "question": f"Q{i}?", "options": ["A", "B", "C", "D"], "correct_answer": 0, "explanation": ""}
        for i in range(n)
    ]


class TestRecordQuizResult:
    def test_correct_points_beginner(self):
        questions = _make_questions(10)
        answers = [0] * 10  # all correct
        result = data_manager.record_quiz_result(questions, answers, "beginner")
        assert result["correct_count"] == 10
        assert result["points_earned"] == 10 * 10  # 10 pts/correct at beginner

    def test_partial_correct(self):
        questions = _make_questions(4)
        answers = [0, 1, 1, 1]  # only first correct
        result = data_manager.record_quiz_result(questions, answers, "beginner")
        assert result["correct_count"] == 1
        assert result["points_earned"] == 10

    def test_intermediate_points(self):
        questions = _make_questions(2)
        answers = [0, 0]
        result = data_manager.record_quiz_result(questions, answers, "intermediate")
        assert result["points_earned"] == 2 * 15

    def test_advanced_points(self):
        questions = _make_questions(2)
        answers = [0, 0]
        result = data_manager.record_quiz_result(questions, answers, "advanced")
        assert result["points_earned"] == 2 * 25

    def test_no_level_up_when_below_threshold(self):
        questions = _make_questions(5)
        answers = [0] * 5  # 50 pts, threshold is 100
        result = data_manager.record_quiz_result(questions, answers, "beginner")
        assert not result["level_up"]
        assert result["new_level"] == "beginner"

    def test_level_up_beginner_to_intermediate(self):
        questions = _make_questions(10)
        answers = [0] * 10  # 100 pts — exactly hits the threshold
        result = data_manager.record_quiz_result(questions, answers, "beginner")
        assert result["level_up"]
        assert result["new_level"] == "intermediate"

    def test_level_up_carries_over_excess_points(self):
        questions = _make_questions(15)
        answers = [0] * 15  # 150 pts — 50 pts over the 100 threshold
        result = data_manager.record_quiz_result(questions, answers, "beginner")
        assert result["level_up"]
        assert result["new_level"] == "intermediate"
        assert result["level_points"] == 50

    def test_multi_level_skip(self):
        """Earning enough points to skip two levels at once should land at advanced."""
        # Need 100 pts (beginner→intermediate) + 200 pts (intermediate→advanced) = 300 pts
        # at beginner rate (10 pts/correct) that's 30 correct answers
        questions = _make_questions(30)
        answers = [0] * 30
        result = data_manager.record_quiz_result(questions, answers, "beginner")
        assert result["new_level"] == "advanced"

    def test_no_level_up_at_max_level(self):
        # Set user to advanced first
        data = data_manager.load_data()
        data["current_level"] = "advanced"
        data["level_points"] = 0
        data_manager.save_data(data)

        questions = _make_questions(10)
        answers = [0] * 10
        result = data_manager.record_quiz_result(questions, answers, "advanced")
        assert not result["level_up"]
        assert result["new_level"] == "advanced"

    def test_topic_stats_updated(self):
        topic = "Statistics and Probability"
        questions = _make_questions(3, topic=topic)
        answers = [0, 0, 1]  # 2 correct
        data_manager.record_quiz_result(questions, answers, "beginner")
        data = data_manager.load_data()
        stats = data["topic_stats"][topic]
        assert stats["total_questions"] == 3
        assert stats["correct_answers"] == 2

    def test_quiz_history_appended(self):
        questions = _make_questions(5)
        answers = [0] * 5
        data_manager.record_quiz_result(questions, answers, "beginner")
        data = data_manager.load_data()
        assert len(data["quiz_history"]) == 1
        record = data["quiz_history"][0]
        assert record["level"] == "beginner"
        assert record["total_questions"] == 5
        assert record["correct_answers"] == 5

    def test_history_does_not_exceed_100_on_repeated_quizzes(self):
        questions = _make_questions(1)
        answers = [0]
        for _ in range(105):
            data_manager.record_quiz_result(questions, answers, "beginner")
        data = data_manager.load_data()
        assert len(data["quiz_history"]) == 100


# ---------------------------------------------------------------------------
# get_weak_topics / get_strong_topics / get_untested_topics
# ---------------------------------------------------------------------------

class TestTopicQueries:
    def _seed_topic(self, topic, total, correct, level="beginner"):
        data = data_manager.load_data()
        data["topic_stats"][topic]["total_questions"] = total
        data["topic_stats"][topic]["correct_answers"] = correct
        data["topic_stats"][topic][level]["total"] = total
        data["topic_stats"][topic][level]["correct"] = correct
        data_manager.save_data(data)

    def test_untested_topics_includes_all_by_default(self):
        untested = data_manager.get_untested_topics()
        from config import ML_TOPICS
        assert set(untested) == set(ML_TOPICS)

    def test_untested_excludes_attempted_topic(self):
        self._seed_topic("Statistics and Probability", total=1, correct=1)
        untested = data_manager.get_untested_topics()
        assert "Statistics and Probability" not in untested

    def test_weak_topics_sorted_by_accuracy(self):
        self._seed_topic("Statistics and Probability", total=10, correct=3)  # 30%
        self._seed_topic("Linear Algebra", total=10, correct=8)               # 80%
        self._seed_topic("Loss Functions", total=10, correct=1)               # 10%
        weak = data_manager.get_weak_topics(limit=3)
        topics = [w["topic"] for w in weak]
        assert topics[0] == "Loss Functions"
        assert topics[1] == "Statistics and Probability"

    def test_weak_topics_limit_respected(self):
        for topic in ["Statistics and Probability", "Linear Algebra", "Loss Functions"]:
            self._seed_topic(topic, total=5, correct=1)
        assert len(data_manager.get_weak_topics(limit=2)) == 2

    def test_strong_topics_requires_min_3_questions(self):
        self._seed_topic("Statistics and Probability", total=2, correct=2)
        strong = data_manager.get_strong_topics()
        assert not any(t["topic"] == "Statistics and Probability" for t in strong)

    def test_strong_topics_sorted_highest_first(self):
        self._seed_topic("Statistics and Probability", total=5, correct=5)   # 100%
        self._seed_topic("Linear Algebra", total=5, correct=3)                # 60%
        strong = data_manager.get_strong_topics(limit=2)
        assert strong[0]["topic"] == "Statistics and Probability"


# ---------------------------------------------------------------------------
# get_level_progress
# ---------------------------------------------------------------------------

class TestLevelProgress:
    def test_beginner_progress_at_zero(self):
        progress = data_manager.get_level_progress()
        assert progress["current_level"] == "beginner"
        assert progress["progress_percent"] == 0.0
        assert progress["is_max_level"] is False

    def test_progress_percent_calculated(self):
        data = data_manager.load_data()
        data["current_level"] = "beginner"
        data["level_points"] = 50
        data_manager.save_data(data)
        progress = data_manager.get_level_progress()
        assert progress["progress_percent"] == 50.0

    def test_advanced_is_max_level(self):
        data = data_manager.load_data()
        data["current_level"] = "advanced"
        data["level_points"] = 999
        data_manager.save_data(data)
        progress = data_manager.get_level_progress()
        assert progress["is_max_level"] is True
        assert progress["progress_percent"] == 100


# ---------------------------------------------------------------------------
# get_overall_stats
# ---------------------------------------------------------------------------

class TestOverallStats:
    def test_zero_stats_by_default(self):
        stats = data_manager.get_overall_stats()
        assert stats["total_quizzes"] == 0
        assert stats["accuracy"] == 0

    def test_accuracy_calculated(self):
        data = data_manager.load_data()
        data["total_questions"] = 10
        data["total_correct"] = 7
        data_manager.save_data(data)
        stats = data_manager.get_overall_stats()
        assert stats["accuracy"] == pytest.approx(70.0)


# ---------------------------------------------------------------------------
# reset_progress
# ---------------------------------------------------------------------------

class TestResetProgress:
    def test_reset_clears_all(self):
        questions = _make_questions(10)
        answers = [0] * 10
        data_manager.record_quiz_result(questions, answers, "beginner")

        data_manager.reset_progress()
        stats = data_manager.get_overall_stats()
        assert stats["total_quizzes"] == 0
        assert stats["total_points"] == 0
        assert stats["current_level"] == "beginner"
