"""ML Interview Prep - Desktop Application."""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import List, Dict, Optional

try:
    import ttkbootstrap as ttk_boot
    from ttkbootstrap.constants import *
except ImportError:
    print("ttkbootstrap not installed. Installing...")
    import subprocess
    subprocess.check_call(["pip", "install", "ttkbootstrap"])
    import ttkbootstrap as ttk_boot
    from ttkbootstrap.constants import *

# Fallback constant definitions (for static analysis)
if 'BOTH' not in dir():
    BOTH = "both"
    YES = True
    X = "x"
    Y = "y"
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    CENTER = "center"
    W = "w"
    E = "e"
    N = "n"
    S = "s"
    NW = "nw"
    NE = "ne"
    SW = "sw"
    SE = "se"
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

from config import ML_TOPICS, DIFFICULTY_LEVELS, QUESTIONS_PER_QUIZ
from data_manager import (
    load_data, get_weak_topics, get_strong_topics, get_untested_topics,
    get_level_progress, get_overall_stats, record_quiz_result, reset_progress
)
from question_generator import (
    generate_questions, generate_scenario_questions, get_scenario_categories,
    SCENARIO_CATEGORIES
)


class MLInterviewPrepApp:
    """Main application class for ML Interview Prep."""
    
    def __init__(self):
        """Initialize the application."""
        self.root = ttk_boot.Window(
            title="ML Interview Prep",
            themename="darkly",
            size=(900, 700),
            resizable=(True, True)
        )
        self.root.minsize(800, 600)
        
        # State variables
        self.current_questions: List[Dict] = []
        self.current_question_idx: int = 0
        self.user_answers: List[int] = []
        self.selected_answer: tk.IntVar = tk.IntVar(value=-1)
        self.quiz_level: str = "beginner"
        self.selected_topics: List[str] = []  # For custom topic filtering
        self.is_scenario_quiz: bool = False  # Track if current quiz is scenario-based
        
        # Create main container
        self.main_container = ttk.Frame(self.root, padding=10)
        self.main_container.pack(fill=BOTH, expand=YES)
        
        # Show home screen
        self.show_home_screen()
    
    def clear_container(self):
        """Clear all widgets from main container."""
        for widget in self.main_container.winfo_children():
            widget.destroy()
    
    def show_home_screen(self):
        """Display the home screen with dashboard."""
        self.clear_container()
        
        # Header
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=X, pady=(0, 20))
        
        title_label = ttk.Label(
            header_frame,
            text="🎯 ML Interview Prep",
            font=("Helvetica", 24, "bold"),
            bootstyle="primary"
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Master Machine Learning concepts for your next interview",
            font=("Helvetica", 12)
        )
        subtitle_label.pack()
        
        # Main content - two columns
        content_frame = ttk.Frame(self.main_container)
        content_frame.pack(fill=BOTH, expand=YES)
        
        # Left column - Level Progress and Stats
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))
        
        self.create_level_progress_card(left_frame)
        self.create_stats_card(left_frame)
        
        # Right column - Actions and Recommendations
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=YES, padx=(10, 0))
        
        self.create_quiz_options_card(right_frame)
        self.create_recommendations_card(right_frame)
        
        # Bottom - Reset button
        bottom_frame = ttk.Frame(self.main_container)
        bottom_frame.pack(fill=X, pady=(20, 0))
        
        reset_btn = ttk.Button(
            bottom_frame,
            text="Reset All Progress",
            command=self.confirm_reset,
            bootstyle="danger-outline"
        )
        reset_btn.pack(side=RIGHT)
    
    def create_level_progress_card(self, parent):
        """Create the level progress card."""
        card = ttk.LabelFrame(parent, text="📊 Level Progress", padding=15)
        card.pack(fill=X, pady=(0, 10))
        
        progress = get_level_progress()
        
        # Current level display
        level_name = progress["level_name"]
        level_color = DIFFICULTY_LEVELS[progress["current_level"]]["color"]
        
        level_label = ttk.Label(
            card,
            text=f"Current Level: {level_name}",
            font=("Helvetica", 16, "bold")
        )
        level_label.pack(anchor=W)
        
        # Progress bar
        if not progress["is_max_level"]:
            progress_frame = ttk.Frame(card)
            progress_frame.pack(fill=X, pady=10)
            
            progress_bar = ttk.Progressbar(
                progress_frame,
                value=progress["progress_percent"],
                length=300,
                mode="determinate",
                bootstyle="success"
            )
            progress_bar.pack(fill=X)
            
            points_text = f"{progress['level_points']} / {progress['points_to_next']} points"
            points_label = ttk.Label(progress_frame, text=points_text)
            points_label.pack(anchor=E, pady=(5, 0))
            
            # Level up message
            if progress["progress_percent"] >= 80:
                close_label = ttk.Label(
                    card,
                    text="🔥 You're close to leveling up! Keep going!",
                    font=("Helvetica", 11, "bold"),
                    bootstyle="warning"
                )
                close_label.pack(anchor=W, pady=(5, 0))
            elif progress["progress_percent"] >= 50:
                close_label = ttk.Label(
                    card,
                    text="💪 Halfway there! You're making great progress!",
                    font=("Helvetica", 11),
                    bootstyle="info"
                )
                close_label.pack(anchor=W, pady=(5, 0))
        else:
            max_label = ttk.Label(
                card,
                text="🏆 You've reached the maximum level! You're an ML expert!",
                font=("Helvetica", 11, "bold"),
                bootstyle="success"
            )
            max_label.pack(anchor=W, pady=(10, 0))
        
        # Total points
        total_label = ttk.Label(
            card,
            text=f"Total Points: {progress['total_points']}",
            font=("Helvetica", 12)
        )
        total_label.pack(anchor=W, pady=(10, 0))
    
    def create_stats_card(self, parent):
        """Create the statistics card."""
        card = ttk.LabelFrame(parent, text="📈 Your Statistics", padding=15)
        card.pack(fill=X, pady=(0, 10))
        
        stats = get_overall_stats()
        
        stats_data = [
            ("Total Quizzes", stats["total_quizzes"]),
            ("Questions Answered", stats["total_questions"]),
            ("Correct Answers", stats["total_correct"]),
            ("Accuracy", f"{stats['accuracy']:.1f}%"),
        ]
        
        for label, value in stats_data:
            row = ttk.Frame(card)
            row.pack(fill=X, pady=2)
            ttk.Label(row, text=label + ":", width=20, anchor=W).pack(side=LEFT)
            ttk.Label(row, text=str(value), font=("Helvetica", 11, "bold")).pack(side=LEFT)
    
    def create_quiz_options_card(self, parent):
        """Create the quiz options card."""
        card = ttk.LabelFrame(parent, text="🚀 Start a Quiz", padding=15)
        card.pack(fill=X, pady=(0, 10))
        
        # Level selection
        level_label = ttk.Label(card, text="Select Difficulty Level:", font=("Helvetica", 11))
        level_label.pack(anchor=W, pady=(0, 10))
        
        levels_frame = ttk.Frame(card)
        levels_frame.pack(fill=X, pady=(0, 15))
        
        progress = get_level_progress()
        current_level = progress["current_level"]
        
        for level_key, level_data in DIFFICULTY_LEVELS.items():
            btn_style = "success" if level_key == "beginner" else ("warning" if level_key == "intermediate" else "danger")
            
            btn = ttk.Button(
                levels_frame,
                text=level_data["name"],
                command=lambda l=level_key: self.start_quiz(l),
                bootstyle=btn_style,
                width=12
            )
            btn.pack(side=LEFT, padx=5)
            
            # Add indicator for current level
            if level_key == current_level:
                indicator = ttk.Label(levels_frame, text="◄", bootstyle="primary")
                indicator.pack(side=LEFT)
        
        # Focus on weak areas button
        ttk.Separator(card, orient=HORIZONTAL).pack(fill=X, pady=15)
        
        weak_topics = get_weak_topics(3)
        if weak_topics:
            weak_btn = ttk.Button(
                card,
                text="🎯 Focus on Weak Areas",
                command=lambda: self.start_quiz(current_level, focus_weak=True),
                bootstyle="info-outline",
                width=25
            )
            weak_btn.pack(pady=5)
        
        # Custom topic selection button
        custom_btn = ttk.Button(
            card,
            text="📝 Select Topics (Custom Quiz)",
            command=self.show_topic_selection,
            bootstyle="secondary-outline",
            width=25
        )
        custom_btn.pack(pady=5)
        
        # Scenario-based questions button
        ttk.Separator(card, orient=HORIZONTAL).pack(fill=X, pady=15)
        
        scenario_label = ttk.Label(
            card,
            text="🧠 Advanced Case Studies (AI-Generated)",
            font=("Helvetica", 10, "bold"),
            bootstyle="warning"
        )
        scenario_label.pack(anchor=W)
        
        scenario_btn = ttk.Button(
            card,
            text="🎭 Scenario & Trick Questions",
            command=self.show_scenario_quiz_options,
            bootstyle="warning-outline",
            width=30
        )
        scenario_btn.pack(pady=5)
    
    def create_recommendations_card(self, parent):
        """Create the recommendations card."""
        card = ttk.LabelFrame(parent, text="💡 Recommendations", padding=15)
        card.pack(fill=BOTH, expand=YES)
        
        # Create scrollable frame
        canvas = tk.Canvas(card, highlightthickness=0)
        scrollbar = ttk.Scrollbar(card, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor=NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Weak topics
        weak_topics = get_weak_topics(5)
        if weak_topics:
            weak_label = ttk.Label(
                scrollable_frame,
                text="📉 Areas to Improve:",
                font=("Helvetica", 11, "bold"),
                bootstyle="danger"
            )
            weak_label.pack(anchor=W, pady=(0, 5))
            
            for topic_data in weak_topics:
                accuracy = topic_data["accuracy"] * 100
                text = f"  • {topic_data['topic']} ({accuracy:.0f}% accuracy)"
                ttk.Label(scrollable_frame, text=text, wraplength=280).pack(anchor=W)
        
        # Untested topics
        untested = get_untested_topics()
        if untested:
            ttk.Label(scrollable_frame, text="").pack()  # Spacer
            untested_label = ttk.Label(
                scrollable_frame,
                text="❓ Topics Not Yet Tested:",
                font=("Helvetica", 11, "bold"),
                bootstyle="warning"
            )
            untested_label.pack(anchor=W, pady=(0, 5))
            
            for topic in untested[:5]:
                ttk.Label(scrollable_frame, text=f"  • {topic}", wraplength=280).pack(anchor=W)
            if len(untested) > 5:
                ttk.Label(scrollable_frame, text=f"  ... and {len(untested) - 5} more").pack(anchor=W)
        
        # Strong topics
        strong_topics = get_strong_topics(3)
        if strong_topics:
            ttk.Label(scrollable_frame, text="").pack()  # Spacer
            strong_label = ttk.Label(
                scrollable_frame,
                text="✅ Your Strong Areas:",
                font=("Helvetica", 11, "bold"),
                bootstyle="success"
            )
            strong_label.pack(anchor=W, pady=(0, 5))
            
            for topic_data in strong_topics:
                accuracy = topic_data["accuracy"] * 100
                text = f"  • {topic_data['topic']} ({accuracy:.0f}%)"
                ttk.Label(scrollable_frame, text=text, wraplength=280).pack(anchor=W)
        
        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)
    
    def show_topic_selection(self):
        """Show topic selection screen for custom quiz."""
        self.clear_container()
        
        # Header
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=X, pady=(0, 20))
        
        title_label = ttk.Label(
            header_frame,
            text="📝 Select Topics for Custom Quiz",
            font=("Helvetica", 18, "bold"),
            bootstyle="primary"
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Choose the topics you want to be tested on",
            font=("Helvetica", 11)
        )
        subtitle_label.pack()
        
        # Topic checkboxes in scrollable frame
        topics_frame = ttk.LabelFrame(self.main_container, text="Available Topics", padding=10)
        topics_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        canvas = tk.Canvas(topics_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(topics_frame, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor=NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create checkbox variables
        self.topic_vars = {}
        
        # Arrange in 2 columns
        for i, topic in enumerate(ML_TOPICS):
            var = tk.BooleanVar(value=False)
            self.topic_vars[topic] = var
            
            row = i // 2
            col = i % 2
            
            cb = ttk.Checkbutton(
                scrollable_frame,
                text=topic,
                variable=var,
                bootstyle="primary-round-toggle"
            )
            cb.grid(row=row, column=col, sticky=W, padx=10, pady=5)
        
        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Selection buttons
        selection_frame = ttk.Frame(self.main_container)
        selection_frame.pack(fill=X, pady=10)
        
        select_all_btn = ttk.Button(
            selection_frame,
            text="Select All",
            command=lambda: self.toggle_all_topics(True),
            bootstyle="info-outline",
            width=15
        )
        select_all_btn.pack(side=LEFT, padx=5)
        
        deselect_all_btn = ttk.Button(
            selection_frame,
            text="Deselect All",
            command=lambda: self.toggle_all_topics(False),
            bootstyle="secondary-outline",
            width=15
        )
        deselect_all_btn.pack(side=LEFT, padx=5)
        
        # Level selection for custom quiz
        level_frame = ttk.LabelFrame(self.main_container, text="Select Difficulty Level", padding=10)
        level_frame.pack(fill=X, pady=10)
        
        self.custom_level_var = tk.StringVar(value="beginner")
        
        for level_key, level_data in DIFFICULTY_LEVELS.items():
            rb = ttk.Radiobutton(
                level_frame,
                text=level_data["name"],
                variable=self.custom_level_var,
                value=level_key,
                bootstyle="primary"
            )
            rb.pack(side=LEFT, padx=20)
        
        # Navigation buttons
        nav_frame = ttk.Frame(self.main_container)
        nav_frame.pack(fill=X, pady=20)
        
        back_btn = ttk.Button(
            nav_frame,
            text="← Back",
            command=self.show_home_screen,
            bootstyle="secondary"
        )
        back_btn.pack(side=LEFT)
        
        start_btn = ttk.Button(
            nav_frame,
            text="Start Custom Quiz →",
            command=self.start_custom_quiz,
            bootstyle="success"
        )
        start_btn.pack(side=RIGHT)
    
    def show_scenario_quiz_options(self):
        """Show scenario quiz category selection."""
        self.clear_container()
        
        # Header
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=X, pady=(0, 20))
        
        title_label = ttk.Label(
            header_frame,
            text="🎭 Scenario & Trick Questions",
            font=("Helvetica", 18, "bold"),
            bootstyle="warning"
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            header_frame,
            text="AI-Generated case-study questions to test deep understanding",
            font=("Helvetica", 11)
        )
        subtitle_label.pack()
        
        # Description
        desc_frame = ttk.LabelFrame(self.main_container, text="About This Section", padding=15)
        desc_frame.pack(fill=X, pady=10)
        
        desc_text = """These are scenario-based questions generated by AI to test:

• Deep conceptual understanding beyond definitions
• Practical problem-solving and debugging skills
• Trade-off analysis and decision making
• Real-world failure mode recognition

Each question presents a realistic scenario and asks you to identify the best approach or diagnose issues.
Questions are generated fresh each time using few-shot learning from curated examples."""
        
        desc_label = ttk.Label(desc_frame, text=desc_text, wraplength=700, justify=LEFT)
        desc_label.pack(anchor=W)
        
        # Number of questions selection
        num_frame = ttk.LabelFrame(self.main_container, text="Number of Questions", padding=15)
        num_frame.pack(fill=X, pady=10)
        
        self.scenario_num_var = tk.IntVar(value=5)
        
        for num in [3, 5, 10]:
            rb = ttk.Radiobutton(
                num_frame,
                text=f"{num} Questions",
                variable=self.scenario_num_var,
                value=num,
                bootstyle="warning"
            )
            rb.pack(side=LEFT, padx=20)
        
        # Category selection
        cat_frame = ttk.LabelFrame(self.main_container, text="Select Category", padding=15)
        cat_frame.pack(fill=BOTH, expand=YES, pady=10)
        
        categories = SCENARIO_CATEGORIES
        
        # All categories button
        all_btn = ttk.Button(
            cat_frame,
            text="🎲 Mixed Categories (Recommended)",
            command=lambda: self.start_scenario_quiz(None),
            bootstyle="primary",
            width=35
        )
        all_btn.pack(pady=5)
        
        ttk.Separator(cat_frame, orient=HORIZONTAL).pack(fill=X, pady=10)
        
        # Category buttons in grid
        cat_grid = ttk.Frame(cat_frame)
        cat_grid.pack(fill=X)
        
        for i, cat in enumerate(categories):
            btn = ttk.Button(
                cat_grid,
                text=cat,
                command=lambda c=cat: self.start_scenario_quiz(c),
                bootstyle="info-outline",
                width=25
            )
            row = i // 2
            col = i % 2
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        cat_grid.columnconfigure(0, weight=1)
        cat_grid.columnconfigure(1, weight=1)
        
        # Navigation
        nav_frame = ttk.Frame(self.main_container)
        nav_frame.pack(fill=X, pady=20)
        
        back_btn = ttk.Button(
            nav_frame,
            text="← Back",
            command=self.show_home_screen,
            bootstyle="secondary"
        )
        back_btn.pack(side=LEFT)
    
    def start_scenario_quiz(self, category: Optional[str] = None):
        """Start a scenario-based quiz using LLM generation."""
        self.is_scenario_quiz = True
        self.quiz_level = "advanced"
        self.current_question_idx = 0
        self.user_answers = []
        self.selected_answer.set(-1)
        
        num_questions = self.scenario_num_var.get() if hasattr(self, 'scenario_num_var') else 5
        
        # Show loading screen
        self.clear_container()
        loading_label = ttk.Label(
            self.main_container,
            text="🔄 Generating scenario questions...\n\nThe AI is creating challenging case-study questions.\nThis may take a moment.",
            font=("Helvetica", 14),
            justify=CENTER
        )
        loading_label.pack(expand=YES)
        
        # Generate questions in background thread
        def generate():
            try:
                questions = generate_scenario_questions(
                    category=category,
                    num_questions=num_questions
                )
                
                if questions:
                    # Convert to standard question format
                    self.current_questions = []
                    for q in questions:
                        self.current_questions.append({
                            "topic": q["topic"],
                            "question": f"{q['scenario']}\n\n{q['question']}",
                            "options": q["options"],
                            "correct_answer": q["correct_answer"],
                            "explanation": q["explanation"],
                            "is_scenario": True
                        })
                    self.root.after(0, self.show_question)
                else:
                    self.root.after(0, lambda: self.show_error("Failed to generate scenario questions. Please try again."))
            except ValueError as e:
                error_msg = str(e)
                self.root.after(0, lambda msg=error_msg: self.show_error(msg))
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                self.root.after(0, lambda msg=error_msg: self.show_error(msg))
        
        thread = threading.Thread(target=generate, daemon=True)
        thread.start()
    
    def toggle_all_topics(self, select: bool):
        """Select or deselect all topics."""
        for var in self.topic_vars.values():
            var.set(select)
    
    def start_custom_quiz(self):
        """Start quiz with selected topics."""
        selected = [topic for topic, var in self.topic_vars.items() if var.get()]
        
        if not selected:
            messagebox.showwarning("No Topics Selected", "Please select at least one topic.")
            return
        
        self.selected_topics = selected
        level = self.custom_level_var.get()
        self.start_quiz(level, custom_topics=selected)
    
    def start_quiz(self, level: str, focus_weak: bool = False, custom_topics: List[str] = None):
        """Start a new quiz."""
        self.quiz_level = level
        self.current_question_idx = 0
        self.user_answers = []
        self.selected_answer.set(-1)
        self.is_scenario_quiz = False  # Reset scenario flag for regular quizzes
        
        # Show loading screen
        self.clear_container()
        loading_label = ttk.Label(
            self.main_container,
            text="🔄 Generating questions...\n\nPlease wait while the AI creates your quiz.",
            font=("Helvetica", 14),
            justify=CENTER
        )
        loading_label.pack(expand=YES)
        
        # Generate questions in background thread
        def generate():
            try:
                weak_topics = None
                topics_to_use = None
                
                if custom_topics:
                    # Use custom selected topics
                    topics_to_use = custom_topics
                elif focus_weak:
                    weak_data = get_weak_topics(QUESTIONS_PER_QUIZ)
                    weak_topics = [t["topic"] for t in weak_data]
                
                questions = generate_questions(
                    level=level,
                    topics=topics_to_use,
                    num_questions=QUESTIONS_PER_QUIZ,
                    focus_weak_areas=focus_weak,
                    weak_topics=weak_topics
                )
                
                if questions:
                    self.current_questions = questions
                    self.root.after(0, self.show_question)
                else:
                    self.root.after(0, lambda: self.show_error("Failed to generate questions. Please try again."))
            except ValueError as e:
                error_msg = str(e)
                self.root.after(0, lambda msg=error_msg: self.show_error(msg))
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                self.root.after(0, lambda msg=error_msg: self.show_error(msg))
        
        thread = threading.Thread(target=generate, daemon=True)
        thread.start()
    
    def show_error(self, message: str):
        """Show error message and return to home."""
        messagebox.showerror("Error", message)
        self.show_home_screen()
    
    def show_question(self):
        """Display the current question."""
        self.clear_container()
        
        if self.current_question_idx >= len(self.current_questions):
            self.show_results()
            return
        
        question = self.current_questions[self.current_question_idx]
        self.selected_answer.set(-1)
        
        # Header
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=X, pady=(0, 20))
        
        # Progress info
        progress_text = f"Question {self.current_question_idx + 1} of {len(self.current_questions)}"
        ttk.Label(header_frame, text=progress_text, font=("Helvetica", 12)).pack(side=LEFT)
        
        level_name = DIFFICULTY_LEVELS[self.quiz_level]["name"]
        if self.is_scenario_quiz:
            level_display = "Scenario Quiz"
        else:
            level_display = f"Level: {level_name}"
        ttk.Label(
            header_frame,
            text=level_display,
            font=("Helvetica", 12, "bold")
        ).pack(side=RIGHT)
        
        # Progress bar
        progress_val = ((self.current_question_idx) / len(self.current_questions)) * 100
        progress_bar = ttk.Progressbar(
            self.main_container,
            value=progress_val,
            length=400,
            mode="determinate",
            bootstyle="info"
        )
        progress_bar.pack(fill=X, pady=(0, 20))
        
        # Topic badge
        badge_style = "warning" if self.is_scenario_quiz else "secondary"
        badge_prefix = "🎭" if self.is_scenario_quiz else "📚"
        topic_label = ttk.Label(
            self.main_container,
            text=f"{badge_prefix} {question['topic']}",
            font=("Helvetica", 10),
            bootstyle=badge_style
        )
        topic_label.pack(anchor=W, pady=(0, 10))
        
        # Question text - make scrollable for scenario questions
        if self.is_scenario_quiz:
            # Scrollable question frame for longer scenario text
            question_outer = ttk.Frame(self.main_container)
            question_outer.pack(fill=BOTH, expand=YES, pady=(0, 10))
            
            q_canvas = tk.Canvas(question_outer, highlightthickness=0, height=180)
            q_scrollbar = ttk.Scrollbar(question_outer, orient=VERTICAL, command=q_canvas.yview)
            question_frame = ttk.Frame(q_canvas, padding=15)
            
            question_frame.bind(
                "<Configure>",
                lambda e: q_canvas.configure(scrollregion=q_canvas.bbox("all"))
            )
            
            q_canvas.create_window((0, 0), window=question_frame, anchor=NW, width=830)
            q_canvas.configure(yscrollcommand=q_scrollbar.set)
            
            question_label = ttk.Label(
                question_frame,
                text=question["question"],
                font=("Helvetica", 12),
                wraplength=800,
                justify=LEFT
            )
            question_label.pack(anchor=W)
            
            q_canvas.pack(side=LEFT, fill=BOTH, expand=YES)
            q_scrollbar.pack(side=RIGHT, fill=Y)
            
            # Enable mousewheel scrolling for question
            def _on_q_mousewheel(event):
                q_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            q_canvas.bind("<MouseWheel>", _on_q_mousewheel)
        else:
            # Standard question frame
            question_frame = ttk.Frame(self.main_container, padding=20)
            question_frame.pack(fill=X, pady=(0, 20))
            
            question_label = ttk.Label(
                question_frame,
                text=question["question"],
                font=("Helvetica", 14),
                wraplength=750,
                justify=LEFT
            )
            question_label.pack(anchor=W)
        
        # Answer options
        options_frame = ttk.Frame(self.main_container)
        options_frame.pack(fill=X, padx=20)
        
        option_letters = ["A", "B", "C", "D"]
        for i, option in enumerate(question["options"]):
            option_btn = ttk.Radiobutton(
                options_frame,
                text=f"{option_letters[i]}. {option}",
                variable=self.selected_answer,
                value=i,
                bootstyle="info-toolbutton",
            )
            option_btn.pack(anchor=W, pady=8, fill=X)
        
        # Navigation buttons
        nav_frame = ttk.Frame(self.main_container)
        nav_frame.pack(fill=X, pady=30)
        
        quit_btn = ttk.Button(
            nav_frame,
            text="Quit Quiz",
            command=self.confirm_quit_quiz,
            bootstyle="danger-outline"
        )
        quit_btn.pack(side=LEFT)
        
        if self.current_question_idx < len(self.current_questions) - 1:
            next_btn = ttk.Button(
                nav_frame,
                text="Next Question →",
                command=self.next_question,
                bootstyle="primary"
            )
        else:
            next_btn = ttk.Button(
                nav_frame,
                text="Submit Quiz ✓",
                command=self.next_question,
                bootstyle="success"
            )
        next_btn.pack(side=RIGHT)
    
    def next_question(self):
        """Move to the next question."""
        if self.selected_answer.get() == -1:
            messagebox.showwarning("Select Answer", "Please select an answer before continuing.")
            return
        
        self.user_answers.append(self.selected_answer.get())
        self.current_question_idx += 1
        self.show_question()
    
    def confirm_quit_quiz(self):
        """Confirm quitting the quiz."""
        if messagebox.askyesno("Quit Quiz", "Are you sure you want to quit? Your progress will not be saved."):
            self.show_home_screen()
    
    def show_results(self):
        """Show quiz results."""
        self.clear_container()
        
        # Calculate results
        correct_count = sum(
            1 for i, q in enumerate(self.current_questions)
            if self.user_answers[i] == q["correct_answer"]
        )
        total_questions = len(self.current_questions)
        
        # Record results only for non-scenario quizzes
        if self.is_scenario_quiz:
            result = {
                "correct_count": correct_count,
                "total_questions": total_questions,
                "level_up": False,
                "points_earned": 0,
                "points_to_next": None,
                "level_points": 0
            }
        else:
            result = record_quiz_result(
                self.current_questions,
                self.user_answers,
                self.quiz_level
            )
        
        # Header
        if result["level_up"]:
            header_text = "🎉 Level Up!"
            header_style = "success"
        elif result["correct_count"] == result["total_questions"]:
            header_text = "🏆 Perfect Score!"
            header_style = "success"
        elif result["correct_count"] >= result["total_questions"] * 0.7:
            header_text = "✨ Great Job!"
            header_style = "info"
        elif result["correct_count"] >= result["total_questions"] * 0.5:
            header_text = "👍 Good Effort!"
            header_style = "warning"
        else:
            header_text = "📚 Keep Practicing!"
            header_style = "secondary"
        
        header_label = ttk.Label(
            self.main_container,
            text=header_text,
            font=("Helvetica", 28, "bold"),
            bootstyle=header_style
        )
        header_label.pack(pady=(20, 10))
        
        # Level up message
        if result["level_up"]:
            new_level_name = DIFFICULTY_LEVELS[result["new_level"]]["name"]
            level_msg = ttk.Label(
                self.main_container,
                text=f"Congratulations! You've advanced to {new_level_name} level!",
                font=("Helvetica", 14),
                bootstyle="success"
            )
            level_msg.pack(pady=(0, 20))
        
        # Score summary
        score_title = "Scenario Quiz Results" if self.is_scenario_quiz else "Score Summary"
        score_frame = ttk.LabelFrame(self.main_container, text=score_title, padding=20)
        score_frame.pack(fill=X, padx=50, pady=20)
        
        score_text = f"{result['correct_count']} / {result['total_questions']} correct"
        ttk.Label(score_frame, text=score_text, font=("Helvetica", 20, "bold")).pack()
        
        percentage = (result["correct_count"] / result["total_questions"]) * 100
        ttk.Label(score_frame, text=f"{percentage:.0f}%", font=("Helvetica", 16)).pack()
        
        if self.is_scenario_quiz:
            # Scenario quiz - no points, just feedback
            if percentage >= 80:
                feedback = "🌟 Excellent! You have strong scenario analysis skills."
            elif percentage >= 60:
                feedback = "👍 Good understanding. Review the explanations for missed questions."
            else:
                feedback = "📖 These are challenging! Study the detailed explanations below."
            ttk.Label(score_frame, text=feedback, font=("Helvetica", 11), wraplength=400).pack(pady=(10, 0))
        else:
            points_text = f"+{result['points_earned']} points earned!"
            ttk.Label(score_frame, text=points_text, font=("Helvetica", 12), bootstyle="success").pack(pady=(10, 0))
        
        # Progress to next level
        if result["points_to_next"]:
            progress_frame = ttk.Frame(score_frame)
            progress_frame.pack(fill=X, pady=(15, 0))
            
            progress_pct = (result["level_points"] / result["points_to_next"]) * 100
            ttk.Label(progress_frame, text="Progress to next level:").pack()
            
            progress_bar = ttk.Progressbar(
                progress_frame,
                value=progress_pct,
                length=200,
                mode="determinate",
                bootstyle="info"
            )
            progress_bar.pack(pady=5)
            
            remaining = result["points_to_next"] - result["level_points"]
            ttk.Label(progress_frame, text=f"{remaining} points to go").pack()
        
        # Question Review - Scrollable
        review_frame = ttk.LabelFrame(self.main_container, text="Question Review", padding=10)
        review_frame.pack(fill=BOTH, expand=YES, padx=50, pady=10)
        
        canvas = tk.Canvas(review_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(review_frame, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor=NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for i, question in enumerate(self.current_questions):
            user_answer = self.user_answers[i]
            correct_answer = question["correct_answer"]
            is_correct = user_answer == correct_answer
            
            q_frame = ttk.Frame(scrollable_frame, padding=10)
            q_frame.pack(fill=X, pady=5)
            
            # Status icon
            status = "✅" if is_correct else "❌"
            q_header = f"{status} Q{i+1}: {question['question'][:80]}..."
            
            header_label = ttk.Label(
                q_frame,
                text=q_header,
                font=("Helvetica", 10, "bold"),
                wraplength=650
            )
            header_label.pack(anchor=W)
            
            if not is_correct:
                your_ans = f"Your answer: {question['options'][user_answer]}"
                ttk.Label(q_frame, text=your_ans, bootstyle="danger", wraplength=650).pack(anchor=W)
                
                correct_ans = f"Correct answer: {question['options'][correct_answer]}"
                ttk.Label(q_frame, text=correct_ans, bootstyle="success", wraplength=650).pack(anchor=W)
            
            # Explanation
            exp_label = ttk.Label(
                q_frame,
                text=f"💡 {question['explanation']}",
                wraplength=650,
                font=("Helvetica", 9)
            )
            exp_label.pack(anchor=W, pady=(5, 0))
            
            ttk.Separator(q_frame, orient=HORIZONTAL).pack(fill=X, pady=(10, 0))
        
        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Navigation buttons
        nav_frame = ttk.Frame(self.main_container)
        nav_frame.pack(fill=X, padx=50, pady=20)
        
        home_btn = ttk.Button(
            nav_frame,
            text="← Back to Home",
            command=self.show_home_screen,
            bootstyle="secondary"
        )
        home_btn.pack(side=LEFT)
        
        if self.is_scenario_quiz:
            retry_btn = ttk.Button(
                nav_frame,
                text="More Scenario Questions →",
                command=self.show_scenario_quiz_options,
                bootstyle="warning"
            )
        else:
            retry_btn = ttk.Button(
                nav_frame,
                text="Take Another Quiz →",
                command=lambda: self.start_quiz(self.quiz_level),
                bootstyle="primary"
            )
        retry_btn.pack(side=RIGHT)
    
    def confirm_reset(self):
        """Confirm resetting all progress."""
        if messagebox.askyesno(
            "Reset Progress",
            "Are you sure you want to reset all progress? This cannot be undone."
        ):
            reset_progress()
            self.show_home_screen()
            messagebox.showinfo("Reset Complete", "Your progress has been reset.")
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    app = MLInterviewPrepApp()
    app.run()


if __name__ == "__main__":
    main()
