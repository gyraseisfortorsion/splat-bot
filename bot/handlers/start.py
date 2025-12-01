"""Start and menu handlers"""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models import User
from ..database.db import async_session_maker
from ..keyboards.inline import get_main_menu, get_quiz_topics, get_splat_test_types, get_back_button

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command"""
    async with async_session_maker() as session:
        # Get or create user
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name
            )
            session.add(user)
            await session.commit()

    welcome_text = f"""
🎓 <b>Welcome to SPLAT Final Exam Prep Bot!</b>

Hi {message.from_user.first_name}! Ready to ace your CSCI 501 final exam?

<b>What this bot offers:</b>
📚 200+ practice questions across all exam topics
💡 102 real SPLAT test cases with detailed explanations
📊 Progress tracking and statistics
✨ Instant feedback with comprehensive explanations

<b>Topics Covered:</b>
• Lexer (Phase 1) - Tokenization & LexException
• Parser (Phase 2) - AST & ParseException
• Semantics (Phase 3) - Type checking & SemanticAnalysisException
• Executor (Phase 4) - Runtime & ExecutionException
• CFG & BNF Grammar
• Grammar Ambiguity
• Java OOP Basics
• Programming Language Concepts

<b>Quick Start:</b>
🎯 Click "Start Quiz" to practice by topic
📚 Click "SPLAT Tests" for real test case questions
📊 Click "My Stats" to track your progress

Good luck with your exam! 🚀
"""

    await message.answer(
        welcome_text,
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Handle /menu command"""
    await message.answer(
        "📚 <b>Main Menu</b>\n\nChoose an option:",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Handle back to menu button"""
    await callback.message.edit_text(
        "📚 <b>Main Menu</b>\n\nChoose an option:",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "menu_quiz")
async def menu_quiz(callback: CallbackQuery):
    """Show quiz topics"""
    await callback.message.edit_text(
        "📚 <b>Select Quiz Topic</b>\n\n"
        "Choose a topic to practice with 10 random questions:\n\n"
        "Each quiz will test your knowledge with MCQ questions and detailed explanations.",
        reply_markup=get_quiz_topics(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "menu_splat_tests")
async def menu_splat_tests(callback: CallbackQuery):
    """Show SPLAT test types"""
    await callback.message.edit_text(
        "💡 <b>SPLAT Test Practice</b>\n\n"
        "Practice with real SPLAT test cases from your project!\n\n"
        "<b>Test Types:</b>\n"
        "❌ <b>Bad Lex:</b> Invalid characters (8 tests)\n"
        "❌ <b>Bad Parse:</b> Syntax errors (22 tests)\n"
        "❌ <b>Bad Semantics:</b> Type/scope errors (34 tests)\n"
        "❌ <b>Bad Execution:</b> Runtime errors (1 test)\n"
        "✅ <b>Good Execution:</b> Successful programs (37 tests)\n\n"
        "Each question shows the SPLAT code and asks you to predict the exception type or output.",
        reply_markup=get_splat_test_types(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    """Show help information"""
    help_text = """
📚 <b>SPLAT Exam Bot - Help</b>

<b>Commands:</b>
/start - Welcome message and main menu
/menu - Show main menu
/stats - View your statistics
/help - Show this help message

<b>How to Use:</b>
1️⃣ Choose a quiz type or topic from the menu
2️⃣ Answer questions by clicking the options
3️⃣ Get instant feedback with explanations
4️⃣ Track your progress with /stats

<b>Question Types:</b>
• Multiple choice questions (MCQ)
• SPLAT code analysis (predict exceptions/output)
• Grammar and parsing questions
• Java and OOP concepts

<b>Tips for Success:</b>
✅ Practice daily for consistent improvement
✅ Review explanations carefully
✅ Try all topic quizzes, not just your weak areas
✅ Use SPLAT test questions to understand real examples
✅ Track your accuracy and improve weak topics

<b>Topics Covered:</b>
- Programming language concepts
- CFG, BNF, and grammar ambiguity
- Lexer, Parser, Semantics, Executor
- SPLAT language and exceptions
- Java OOP basics

Need more help? Contact your instructor or TA!
"""

    await callback.message.edit_text(
        help_text,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    help_text = """
📚 <b>SPLAT Exam Bot - Help</b>

<b>Commands:</b>
/start - Welcome message and main menu
/menu - Show main menu
/stats - View your statistics
/help - Show this help message

<b>How to Use:</b>
1️⃣ Choose a quiz type or topic from the menu
2️⃣ Answer questions by clicking the options
3️⃣ Get instant feedback with explanations
4️⃣ Track your progress with /stats

Good luck with your exam! 🚀
"""

    await message.answer(
        help_text,
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
