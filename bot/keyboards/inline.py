"""Inline keyboards for SPLAT Exam Bot"""
import random
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu() -> InlineKeyboardMarkup:
    """Main menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="📚 Start Quiz", callback_data="menu_quiz"),
            InlineKeyboardButton(text="💡 SPLAT Tests", callback_data="menu_splat_tests")
        ],
        [
            InlineKeyboardButton(text="📊 My Stats", callback_data="my_stats"),
            InlineKeyboardButton(text="❓ Help", callback_data="help")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_quiz_topics() -> InlineKeyboardMarkup:
    """Quiz topics selection keyboard"""
    keyboard = [
        [InlineKeyboardButton(text="🔤 Lexer (Phase 1)", callback_data="quiz_lexer")],
        [InlineKeyboardButton(text="🌳 Parser (Phase 2)", callback_data="quiz_parser")],
        [InlineKeyboardButton(text="🔍 Semantics (Phase 3)", callback_data="quiz_semantics")],
        [InlineKeyboardButton(text="⚡ Executor (Phase 4)", callback_data="quiz_executor")],
        [InlineKeyboardButton(text="📝 CFG & Grammar", callback_data="quiz_cfg")],
        [InlineKeyboardButton(text="☕ Java Basics", callback_data="quiz_java")],
        [InlineKeyboardButton(text="🎲 Mixed (All Topics)", callback_data="quiz_mixed")],
        [InlineKeyboardButton(text="« Back to Menu", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_splat_test_types() -> InlineKeyboardMarkup:
    """SPLAT test types selection"""
    keyboard = [
        [InlineKeyboardButton(text="❌ Lex Exceptions (8 tests)", callback_data="splat_badlex")],
        [InlineKeyboardButton(text="❌ Parse Exceptions (22 tests)", callback_data="splat_badparse")],
        [InlineKeyboardButton(text="❌ Semantic Exceptions (34 tests)", callback_data="splat_badsemantics")],
        [InlineKeyboardButton(text="❌ Execution Exceptions (1 test)", callback_data="splat_badexecution")],
        [InlineKeyboardButton(text="✅ Good Execution (37 tests)", callback_data="splat_goodexecution")],
        [InlineKeyboardButton(text="🎲 Random SPLAT Test", callback_data="splat_random")],
        [InlineKeyboardButton(text="« Back to Menu", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_learn_topics() -> InlineKeyboardMarkup:
    """Learning topics selection"""
    keyboard = [
        [InlineKeyboardButton(text="📚 CFG & BNF Notation", callback_data="learn_cfg")],
        [InlineKeyboardButton(text="🔤 Lexical Analysis", callback_data="learn_lexer")],
        [InlineKeyboardButton(text="🌳 Parsing & AST", callback_data="learn_parser")],
        [InlineKeyboardButton(text="🔍 Semantic Analysis", callback_data="learn_semantics")],
        [InlineKeyboardButton(text="⚡ Code Execution", callback_data="learn_executor")],
        [InlineKeyboardButton(text="☕ Java OOP Concepts", callback_data="learn_java")],
        [InlineKeyboardButton(text="🎯 SPLAT Language", callback_data="learn_splat")],
        [InlineKeyboardButton(text="« Back to Menu", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_quiz_navigation(current_q: int, total_q: int, question_id: int) -> InlineKeyboardMarkup:
    """Navigation buttons during quiz"""
    keyboard = [
        [InlineKeyboardButton(
            text=f"📊 Progress: {current_q}/{total_q}",
            callback_data="show_progress"
        )],
        [
            InlineKeyboardButton(text="❌ End Quiz", callback_data="end_quiz"),
            InlineKeyboardButton(text="⏭ Skip Question", callback_data=f"skip_{question_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_answer_options(question) -> InlineKeyboardMarkup:
    """Create poll-style answer buttons with shuffled options"""
    keyboard = []
    options = ['A', 'B', 'C', 'D', 'E']
    option_texts = [
        question.option_a,
        question.option_b,
        question.option_c,
        question.option_d,
        question.option_e
    ]

    # Create list of (option_letter, option_text) pairs, filtering out empty options
    options_with_text = [(opt, text) for opt, text in zip(options, option_texts) if text]

    # Shuffle the options
    random.shuffle(options_with_text)

    # Create buttons with shuffled options
    for opt, text in options_with_text:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{text[:60]}{'...' if len(text) > 60 else ''}",
                callback_data=f"answer_{question.id}_{opt}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_explanation_keyboard() -> InlineKeyboardMarkup:
    """Keyboard after showing explanation"""
    keyboard = [
        [
            InlineKeyboardButton(text="➡️ Next Question", callback_data="next_question"),
            InlineKeyboardButton(text="❌ End Quiz", callback_data="end_quiz")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_button() -> InlineKeyboardMarkup:
    """Simple back button"""
    keyboard = [[InlineKeyboardButton(text="« Back to Menu", callback_data="back_to_menu")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
