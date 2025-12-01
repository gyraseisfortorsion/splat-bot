# SPLAT Final Exam Prep Telegram Bot

Comprehensive Telegram bot for preparing for CSCI 501 SPLAT final exam with interactive MCQ questions, polls, and detailed explanations.

## Features

- **200+ Practice Questions** across all exam topics
- **Interactive Telegram Polls** with instant feedback
- **Detailed Explanations** for every answer
- **102 Real SPLAT Test Cases** with exception analysis
- **Progress Tracking** and statistics
- **Daily Challenges** for consistent practice
- **Topic-Specific Quizzes** (Lexer, Parser, Semantics, Executor, CFG, etc.)

## Topics Covered

1. **Programming Language Concepts** (compiled vs interpreted, memory management)
2. **Context-Free Grammars (CFG)** and BNF notation
3. **Grammar Ambiguity** - how to prove it
4. **SPLAT Grammar** and syntax rules
5. **SPLAT Semantics** - type checking, scope rules
6. **Lexer Phase** - tokenization, character handling, LexException
7. **Parser Phase** - recursive descent, parse trees, ParseException
8. **Semantic Analyzer** - type checking, SemanticAnalysisException
9. **Executor Phase** - runtime execution, ExecutionException
10. **Java Basics** - OOP, exceptions, collections
11. **SPLAT Code Analysis** - predict exceptions and outputs

## Setup

### Prerequisites
- Docker and Docker Compose
- Telegram Bot Token (from @BotFather)

### Installation

1. Clone the repository
2. Copy `.env.example` to `.env` and add your bot token:
   ```bash
   cp .env.example .env
   # Edit .env and add your BOT_TOKEN
   ```

3. Run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Start chatting with your bot on Telegram!

## Bot Commands

- `/start` - Welcome message and quick start guide
- `/menu` - Main menu with all options
- `/quiz [topic]` - Start a quiz on specific topic (10 random questions)
- `/practice` - Mixed practice from all topics
- `/daily` - Daily challenge (5 random questions)
- `/splat_test [type]` - Practice with real SPLAT tests
  - Types: `badlex`, `badparse`, `badsemantics`, `badexecution`, `goodexecution`
- `/explain [topic]` - Get theory explanation
- `/stats` - View your progress and scores
- `/help` - Show all available commands

## Question Categories

### SPLAT Test Questions (102 total)
- 8 Lex Exception tests
- 22 Parse Exception tests
- 34 Semantic Exception tests
- 1 Execution Exception test
- 37 Good Execution tests (predict output)

### Conceptual Questions (100+)
- CFG and BNF notation
- Grammar ambiguity proofs
- Compiler phase roles
- Java OOP concepts
- SPLAT semantics

## Development

### Local Setup (without Docker)

1. Install uv package manager:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Install dependencies:
   ```bash
   uv pip install -r pyproject.toml
   ```

3. Run the bot:
   ```bash
   python -m bot.main
   ```

## Project Structure

```
splat-exam-bot/
├── bot/
│   ├── main.py                 # Bot startup
│   ├── handlers/               # Command and callback handlers
│   ├── keyboards/              # Inline and reply keyboards
│   ├── database/               # Database models and connection
│   ├── questions/              # Question JSON files
│   └── utils/                  # Helper functions
├── data/
│   └── splat_tests/            # 102 SPLAT test files
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## License

Created for CSCI 501 Final Exam Preparation
