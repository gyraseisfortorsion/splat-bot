"""Question loader - Load questions from JSON files into database"""
import json
import os
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.models import Question


class QuestionLoader:
    """Load questions from JSON files"""

    def __init__(self, questions_dir: str = None):
        if questions_dir is None:
            # Get directory of this file
            this_dir = Path(__file__).parent
            self.questions_dir = this_dir
        else:
            self.questions_dir = Path(questions_dir)

    def load_json_file(self, filename: str) -> list:
        """Load questions from a JSON file"""
        filepath = self.questions_dir / filename
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {filepath} not found")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing {filepath}: {e}")
            return []

    async def load_all_questions(self, session: AsyncSession):
        """Load all questions from JSON files into database"""
        question_files = [
            'splat_tests.json',
            'cfg_grammar.json',
            'compiler_phases.json',
            'java_basics.json'
        ]

        total_loaded = 0

        for filename in question_files:
            questions_data = self.load_json_file(filename)
            for q_data in questions_data:
                # Check if question already exists
                result = await session.execute(
                    select(Question).where(
                        Question.source_file == q_data.get('source_file'),
                        Question.question_text == q_data.get('question_text')
                    )
                )
                existing = result.scalar_one_or_none()

                if not existing:
                    question = Question(
                        category=q_data.get('category'),
                        subcategory=q_data.get('subcategory'),
                        question_text=q_data.get('question_text'),
                        code=q_data.get('code'),
                        option_a=q_data.get('option_a'),
                        option_b=q_data.get('option_b'),
                        option_c=q_data.get('option_c'),
                        option_d=q_data.get('option_d'),
                        option_e=q_data.get('option_e'),
                        correct_answer=q_data.get('correct_answer'),
                        explanation=q_data.get('explanation'),
                        difficulty=q_data.get('difficulty', 'medium'),
                        source_file=q_data.get('source_file'),
                        line_number=q_data.get('line_number'),
                        column_number=q_data.get('column_number')
                    )
                    session.add(question)
                    total_loaded += 1

        await session.commit()
        print(f"Loaded {total_loaded} new questions into database")
        return total_loaded

    async def get_questions_by_category(
        self,
        session: AsyncSession,
        category: str,
        limit: int = 10
    ) -> list:
        """Get random questions by category"""
        from sqlalchemy import func

        result = await session.execute(
            select(Question)
            .where(Question.category == category)
            .order_by(func.random())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_questions_by_subcategory(
        self,
        session: AsyncSession,
        subcategory: str,
        limit: int = 10
    ) -> list:
        """Get random questions by subcategory"""
        from sqlalchemy import func

        result = await session.execute(
            select(Question)
            .where(Question.subcategory == subcategory)
            .order_by(func.random())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_random_questions(
        self,
        session: AsyncSession,
        limit: int = 10
    ) -> list:
        """Get random questions from all categories"""
        from sqlalchemy import func

        result = await session.execute(
            select(Question)
            .order_by(func.random())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_question_by_id(
        self,
        session: AsyncSession,
        question_id: int
    ) -> Question:
        """Get a specific question by ID"""
        result = await session.execute(
            select(Question).where(Question.id == question_id)
        )
        return result.scalar_one_or_none()

    async def get_splat_random_questions(
        self,
        session: AsyncSession,
        limit: int = 20
    ) -> list:
        """Get random questions from SPLAT tests (all subcategories)"""
        from sqlalchemy import func

        # Get questions from SPLAT subcategories
        splat_subcategories = ['badlex', 'badparse', 'badsemantics', 'badexecution', 'goodexecution']

        result = await session.execute(
            select(Question)
            .where(Question.subcategory.in_(splat_subcategories))
            .order_by(func.random())
            .limit(limit)
        )
        return result.scalars().all()
