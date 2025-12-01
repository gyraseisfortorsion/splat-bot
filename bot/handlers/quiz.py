"""Quiz handlers"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from datetime import datetime

from ..database.models import User, UserAnswer, Quiz
from ..database.db import async_session_maker
from ..questions.loader import QuestionLoader
from ..keyboards.inline import (
    get_answer_options,
    get_explanation_keyboard,
    get_back_button,
    get_main_menu
)

router = Router()


class QuizStates(StatesGroup):
    """States for quiz flow"""
    in_quiz = State()
    answering = State()
    viewing_explanation = State()


# Mapping of callback_data to category/subcategory
QUIZ_CATEGORIES = {
    'quiz_lexer': ('lexer', None),
    'quiz_parser': ('parser', None),
    'quiz_semantics': ('semantics', None),
    'quiz_executor': ('executor', None),
    'quiz_cfg': ('cfg', None),
    'quiz_java': ('java', None),
    'quiz_mixed': (None, None),
    'splat_badlex': ('lexer', 'badlex'),
    'splat_badparse': ('parser', 'badparse'),
    'splat_badsemantics': ('semantics', 'badsemantics'),
    'splat_badexecution': ('executor', 'badexecution'),
    'splat_goodexecution': ('executor', 'goodexecution'),
    'splat_random': ('splat', None),
}


@router.callback_query(F.data.in_(QUIZ_CATEGORIES.keys()))
async def start_quiz(callback: CallbackQuery, state: FSMContext):
    """Start a quiz based on selected category"""
    category, subcategory = QUIZ_CATEGORIES[callback.data]

    async with async_session_maker() as session:
        loader = QuestionLoader()

        # Load questions based on category/subcategory
        if subcategory:
            questions = await loader.get_questions_by_subcategory(session, subcategory, limit=10)
        elif category:
            questions = await loader.get_questions_by_category(session, category, limit=10)
        else:
            questions = await loader.get_random_questions(session, limit=10)

        if not questions:
            await callback.message.edit_text(
                "❌ No questions available for this category yet.\n\n"
                "Please try another topic or contact the developer.",
                reply_markup=get_back_button()
            )
            await callback.answer()
            return

        # Create quiz session
        user_result = await session.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        user = user_result.scalar_one()

        quiz = Quiz(
            user_id=user.id,
            quiz_type='topic',
            category=category or 'mixed',
            total_questions=len(questions)
        )
        session.add(quiz)
        await session.commit()

        # Store quiz data in state
        await state.update_data(
            quiz_id=quiz.id,
            questions=[q.id for q in questions],
            current_index=0,
            correct_count=0,
            start_time=datetime.utcnow().timestamp()
        )

    await state.set_state(QuizStates.in_quiz)
    await show_question(callback.message, state, edit=True)
    await callback.answer()


async def show_question(message, state: FSMContext, edit: bool = False):
    """Show current question"""
    data = await state.get_data()
    current_index = data['current_index']
    questions = data['questions']

    if current_index >= len(questions):
        # Quiz complete
        await end_quiz(message, state, edit=edit)
        return

    async with async_session_maker() as session:
        loader = QuestionLoader()
        question = await loader.get_question_by_id(session, questions[current_index])

        # Format question text
        question_text = f"📝 <b>Question {current_index + 1}/{len(questions)}</b>\n\n"

        if question.code:
            question_text += f"<b>{question.question_text}</b>\n\n"
            question_text += f"<pre>{question.code}</pre>\n\n"
        else:
            question_text += f"{question.question_text}\n\n"

        question_text += "Select your answer:"

        if edit:
            await message.edit_text(
                question_text,
                reply_markup=get_answer_options(question),
                parse_mode="HTML"
            )
        else:
            await message.answer(
                question_text,
                reply_markup=get_answer_options(question),
                parse_mode="HTML"
            )


@router.callback_query(F.data.startswith("answer_"))
async def process_answer(callback: CallbackQuery, state: FSMContext):
    """Process user's answer"""
    # Parse callback data: answer_{question_id}_{selected_option}
    parts = callback.data.split('_')
    question_id = int(parts[1])
    selected_option = parts[2]

    data = await state.get_data()
    current_time = datetime.utcnow().timestamp()
    time_taken = int(current_time - data.get('question_start_time', current_time))

    async with async_session_maker() as session:
        # Get question
        loader = QuestionLoader()
        question = await loader.get_question_by_id(session, question_id)

        # Check if answer is correct
        is_correct = (selected_option == question.correct_answer)

        # Update state
        if is_correct:
            correct_count = data.get('correct_count', 0) + 1
            await state.update_data(correct_count=correct_count)

        # Get user
        user_result = await session.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        user = user_result.scalar_one()

        # Record answer
        user_answer = UserAnswer(
            user_id=user.id,
            question_id=question_id,
            selected_answer=selected_option,
            is_correct=is_correct,
            time_taken_seconds=time_taken
        )
        session.add(user_answer)

        # Update user stats
        user.total_questions_answered += 1
        if is_correct:
            user.correct_answers += 1
            user.current_streak += 1
            if user.current_streak > user.best_streak:
                user.best_streak = user.current_streak
        else:
            user.current_streak = 0

        await session.commit()

    # Show explanation
    selected_text = question.get_options()[ord(selected_option) - ord('A')]
    correct_text = question.get_correct_option_text()

    result_emoji = "✅" if is_correct else "❌"
    result_text = f"{result_emoji} <b>{'Correct!' if is_correct else 'Incorrect'}</b>\n\n"

    if not is_correct:
        result_text += f"<b>Your answer:</b> {selected_option}) {selected_text}\n"
        result_text += f"<b>Correct answer:</b> {question.correct_answer}) {correct_text}\n\n"

    result_text += f"<b>📖 Explanation:</b>\n{question.explanation}\n\n"

    if question.source_file:
        result_text += f"<i>Source: {question.source_file}</i>"

    await callback.message.edit_text(
        result_text,
        reply_markup=get_explanation_keyboard(),
        parse_mode="HTML"
    )

    await callback.answer()


@router.callback_query(F.data == "next_question")
async def next_question(callback: CallbackQuery, state: FSMContext):
    """Move to next question"""
    data = await state.get_data()
    current_index = data['current_index'] + 1

    await state.update_data(
        current_index=current_index,
        question_start_time=datetime.utcnow().timestamp()
    )

    await show_question(callback.message, state, edit=True)
    await callback.answer()


@router.callback_query(F.data == "end_quiz")
async def end_quiz_callback(callback: CallbackQuery, state: FSMContext):
    """End quiz from callback"""
    await end_quiz(callback.message, state, edit=True)
    await callback.answer("Quiz ended!")


async def end_quiz(message, state: FSMContext, edit: bool = False):
    """End quiz and show results"""
    data = await state.get_data()
    quiz_id = data.get('quiz_id')
    correct_count = data.get('correct_count', 0)
    total_questions = len(data.get('questions', []))

    if total_questions == 0:
        await state.clear()
        return

    score = (correct_count / total_questions) * 100

    async with async_session_maker() as session:
        # Update quiz record
        quiz_result = await session.execute(
            select(Quiz).where(Quiz.id == quiz_id)
        )
        quiz = quiz_result.scalar_one()

        quiz.completed_at = datetime.utcnow()
        quiz.correct_answers = correct_count
        quiz.score = score

        await session.commit()

    # Determine result emoji and message
    if score >= 90:
        emoji = "🏆"
        message_text = "Outstanding!"
    elif score >= 70:
        emoji = "🎉"
        message_text = "Great job!"
    elif score >= 50:
        emoji = "👍"
        message_text = "Good effort!"
    else:
        emoji = "📚"
        message_text = "Keep practicing!"

    result_text = f"""
{emoji} <b>Quiz Complete!</b>

<b>{message_text}</b>

<b>Results:</b>
✅ Correct: {correct_count}/{total_questions}
📊 Score: {score:.1f}%
🎯 Accuracy: {score:.1f}%

{
    "🔥 Perfect score! You really know your stuff!" if score == 100
    else "💪 Keep practicing to improve your score!" if score < 70
    else "🌟 Great work! You're well prepared!"
}

<b>What's next?</b>
• Try another quiz topic
• Review your statistics with /stats
• Take the daily challenge
"""

    await state.clear()

    if edit:
        await message.edit_text(
            result_text,
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            result_text,
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
