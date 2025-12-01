"""Statistics handlers"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy import select, func, cast, Integer
from datetime import datetime, timedelta

from ..database.models import User, UserAnswer, Question
from ..database.db import async_session_maker
from ..keyboards.inline import get_back_button

router = Router()


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Show user statistics"""
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if not user:
            await message.answer("❌ No statistics available yet. Start a quiz to begin tracking your progress!")
            return

        # Get category breakdown
        category_stats = await get_category_stats(session, user.id)

        stats_text = format_stats(user, category_stats)

        await message.answer(
            stats_text,
            parse_mode="HTML",
            reply_markup=get_back_button()
        )


@router.callback_query(F.data == "my_stats")
async def show_stats_callback(callback: CallbackQuery):
    """Show stats from callback"""
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        user = result.scalar_one_or_none()

        if not user:
            await callback.message.edit_text(
                "❌ No statistics available yet. Start a quiz to begin tracking your progress!",
                reply_markup=get_back_button()
            )
            await callback.answer()
            return

        # Get category breakdown
        category_stats = await get_category_stats(session, user.id)

        stats_text = format_stats(user, category_stats)

        await callback.message.edit_text(
            stats_text,
            parse_mode="HTML",
            reply_markup=get_back_button()
        )

    await callback.answer()


async def get_category_stats(session, user_id: int) -> dict:
    """Get statistics breakdown by category"""
    result = await session.execute(
        select(
            Question.category,
            func.count(UserAnswer.id).label('total'),
            func.sum(cast(UserAnswer.is_correct, Integer)).label('correct')
        )
        .join(UserAnswer, UserAnswer.question_id == Question.id)
        .where(UserAnswer.user_id == user_id)
        .group_by(Question.category)
    )

    stats = {}
    for row in result:
        category = row.category
        total = row.total
        correct = row.correct or 0
        accuracy = (correct / total * 100) if total > 0 else 0

        stats[category] = {
            'total': total,
            'correct': correct,
            'accuracy': accuracy
        }

    return stats


def format_stats(user: User, category_stats: dict) -> str:
    """Format statistics message"""
    stats_text = f"""
📊 <b>Your Statistics</b>

<b>👤 User:</b> {user.first_name}
<b>📅 Member since:</b> {user.created_at.strftime('%B %d, %Y')}

<b>📈 Overall Performance:</b>
✅ <b>Correct Answers:</b> {user.correct_answers}/{user.total_questions_answered}
📊 <b>Accuracy:</b> {user.accuracy:.1f}%
🔥 <b>Current Streak:</b> {user.current_streak}
🏆 <b>Best Streak:</b> {user.best_streak}

"""

    if category_stats:
        stats_text += "<b>📚 Performance by Topic:</b>\n"

        # Category emoji mapping
        category_emojis = {
            'lexer': '🔤',
            'parser': '🌳',
            'semantics': '🔍',
            'executor': '⚡',
            'cfg': '📝',
            'java': '☕',
            'concepts': '💡',
            'splat': '💻'
        }

        # Sort by accuracy (descending)
        sorted_categories = sorted(
            category_stats.items(),
            key=lambda x: x[1]['accuracy'],
            reverse=True
        )

        for category, data in sorted_categories:
            emoji = category_emojis.get(category, '📖')
            category_name = category.capitalize()

            accuracy_emoji = (
                "🌟" if data['accuracy'] >= 90
                else "✨" if data['accuracy'] >= 70
                else "👍" if data['accuracy'] >= 50
                else "📚"
            )

            stats_text += f"\n{emoji} <b>{category_name}:</b> {data['correct']}/{data['total']} ({data['accuracy']:.1f}%) {accuracy_emoji}"

    else:
        stats_text += "\n<i>No category statistics yet. Complete some quizzes to see detailed stats!</i>"

    stats_text += "\n\n💪 <b>Keep practicing to improve your scores!</b>"

    return stats_text
