"""Database models for SPLAT Exam Bot"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User model to track telegram users"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Stats
    total_questions_answered = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    best_streak = Column(Integer, default=0)

    # Relationships
    answers = relationship("UserAnswer", back_populates="user", cascade="all, delete-orphan")

    @property
    def accuracy(self) -> float:
        """Calculate user's overall accuracy"""
        if self.total_questions_answered == 0:
            return 0.0
        return (self.correct_answers / self.total_questions_answered) * 100


class Question(Base):
    """Question model"""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    category = Column(String(50), nullable=False, index=True)  # lexer, parser, semantics, etc.
    subcategory = Column(String(50), nullable=True)  # badlex, badparse, etc.
    question_text = Column(Text, nullable=False)
    code = Column(Text, nullable=True)  # For SPLAT code questions
    option_a = Column(String(500), nullable=False)
    option_b = Column(String(500), nullable=False)
    option_c = Column(String(500), nullable=True)
    option_d = Column(String(500), nullable=True)
    option_e = Column(String(500), nullable=True)
    correct_answer = Column(String(1), nullable=False)  # A, B, C, D, or E
    explanation = Column(Text, nullable=False)
    difficulty = Column(String(20), default="medium")  # easy, medium, hard
    source_file = Column(String(255), nullable=True)  # For SPLAT test questions
    line_number = Column(Integer, nullable=True)  # Where error occurs
    column_number = Column(Integer, nullable=True)  # Where error occurs

    # Relationships
    answers = relationship("UserAnswer", back_populates="question")

    def get_options(self) -> list:
        """Return list of all options"""
        options = [self.option_a, self.option_b]
        if self.option_c:
            options.append(self.option_c)
        if self.option_d:
            options.append(self.option_d)
        if self.option_e:
            options.append(self.option_e)
        return options

    def get_correct_option_text(self) -> str:
        """Get the text of the correct option"""
        option_map = {
            'A': self.option_a,
            'B': self.option_b,
            'C': self.option_c,
            'D': self.option_d,
            'E': self.option_e
        }
        return option_map.get(self.correct_answer, "")


class UserAnswer(Base):
    """Track user answers for statistics"""
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    selected_answer = Column(String(1), nullable=False)  # A, B, C, D, or E
    is_correct = Column(Boolean, nullable=False)
    answered_at = Column(DateTime, default=datetime.utcnow)
    time_taken_seconds = Column(Integer, nullable=True)  # How long to answer

    # Relationships
    user = relationship("User", back_populates="answers")
    question = relationship("Question", back_populates="answers")


class Quiz(Base):
    """Track quiz sessions"""
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_type = Column(String(50), nullable=False)  # daily, practice, topic-specific
    category = Column(String(50), nullable=True)  # If topic-specific
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    score = Column(Float, default=0.0)  # Percentage

    # Relationships
    user = relationship("User")

    @property
    def is_completed(self) -> bool:
        """Check if quiz is completed"""
        return self.completed_at is not None
