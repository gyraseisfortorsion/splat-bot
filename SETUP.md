# SPLAT Exam Bot - Setup Guide

## Prerequisites

1. **Python 3.11+** installed
2. **Docker and Docker Compose** (for containerized deployment)
3. **Telegram Bot Token** from [@BotFather](https://t.me/botfather)

## Quick Start (Docker - Recommended)

### 1. Get Your Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the instructions
3. Choose a name (e.g., "SPLAT Exam Helper")
4. Choose a username (e.g., "splat_exam_bot")
5. Copy the bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Configure Environment

```bash
cd splat-exam-bot
cp .env.example .env
nano .env  # or use any text editor
```

Add your bot token to `.env`:
```
BOT_TOKEN=your_bot_token_here
DATABASE_URL=sqlite+aiosqlite:///data/bot.db
REDIS_URL=redis://redis:6379/0
```

### 3. Run with Docker Compose

```bash
docker-compose up -d
```

That's it! Your bot is now running.

### 4. Check Logs

```bash
docker-compose logs -f bot
```

### 5. Stop the Bot

```bash
docker-compose down
```

## Local Development Setup (without Docker)

### 1. Install uv Package Manager

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Install Dependencies

```bash
cd splat-exam-bot
uv pip install -r pyproject.toml
```

### 3. Set Environment Variables

```bash
cp .env.example .env
# Edit .env and add your BOT_TOKEN
```

### 4. Run the Bot

```bash
python3 -m bot.main
```

## Using the Bot

### Basic Commands

- `/start` - Start the bot and see welcome message
- `/menu` - Show main menu
- `/stats` - View your statistics
- `/daily` - Get daily challenge
- `/help` - Show help information

### Quiz Topics

1. **Lexer (Phase 1)** - Tokenization, LexException
2. **Parser (Phase 2)** - AST building, ParseException
3. **Semantics (Phase 3)** - Type checking, SemanticAnalysisException
4. **Executor (Phase 4)** - Runtime execution, ExecutionException
5. **CFG & Grammar** - Context-Free Grammars, BNF, ambiguity
6. **Java Basics** - OOP, exceptions, collections
7. **Mixed** - Questions from all topics

### SPLAT Test Practice

- **Bad Lex** (8 tests) - Invalid character errors
- **Bad Parse** (22 tests) - Syntax errors
- **Bad Semantics** (34 tests) - Type and scope errors
- **Bad Execution** (1 test) - Runtime errors
- **Good Execution** (37 tests) - Successful programs

## Project Structure

```
splat-exam-bot/
├── bot/
│   ├── main.py                   # Bot entry point
│   ├── database/
│   │   ├── models.py             # User, Question, UserAnswer models
│   │   ├── db.py                 # Database connection
│   │   └── __init__.py
│   ├── handlers/
│   │   ├── start.py              # /start, /menu, /help
│   │   ├── quiz.py               # Quiz logic
│   │   ├── stats.py              # /stats command
│   │   └── __init__.py
│   ├── keyboards/
│   │   ├── inline.py             # Inline keyboards
│   │   └── __init__.py
│   ├── questions/
│   │   ├── loader.py             # Load questions from JSON
│   │   ├── splat_tests.json      # 102 SPLAT test questions
│   │   ├── cfg_grammar.json      # CFG questions
│   │   ├── compiler_phases.json  # Compiler concepts
│   │   ├── java_basics.json      # Java OOP questions
│   │   └── __init__.py
│   └── utils/
│       ├── splat_analyzer.py     # SPLAT code analyzer
│       └── __init__.py
├── data/
│   └── splat_tests/              # 102 SPLAT test files
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
```

## Question Database

The bot includes **200+ questions**:

- **102 SPLAT Test Questions** (generated from actual test files)
  - 8 LexException tests
  - 22 ParseException tests
  - 34 SemanticAnalysisException tests
  - 1 ExecutionException test
  - 37 Good execution tests

- **8 CFG & Grammar Questions**
  - CFG definition
  - Ambiguity proofs
  - BNF notation
  - Parse trees

- **12 Compiler Phase Questions**
  - Programming language concepts
  - Lexer, Parser, Semantics, Executor roles
  - SPLAT exceptions

- **10 Java Basics Questions**
  - OOP concepts
  - Inheritance, polymorphism
  - Exceptions
  - Collections

## Troubleshooting

### Bot doesn't respond

1. Check if bot is running: `docker-compose ps`
2. Check logs: `docker-compose logs -f bot`
3. Verify bot token is correct in `.env`
4. Make sure you started the bot with `/start` in Telegram

### Questions not loading

1. Check database initialization in logs
2. Verify JSON files exist in `bot/questions/`
3. Run analyzer manually:
   ```bash
   cd splat-exam-bot
   python3 -c "from bot.utils.splat_analyzer import SplatTestAnalyzer; analyzer = SplatTestAnalyzer('data/splat_tests'); analyzer.save_questions('bot/questions/splat_tests.json')"
   ```

### Database errors

1. Delete old database: `rm data/bot.db`
2. Restart bot: `docker-compose restart bot`
3. Database will be recreated automatically

### Docker issues

1. Rebuild containers: `docker-compose build --no-cache`
2. Remove old containers: `docker-compose down -v`
3. Start fresh: `docker-compose up -d`

## Development

### Adding New Questions

1. Edit the appropriate JSON file in `bot/questions/`
2. Follow the format:
   ```json
   {
     "category": "lexer",
     "subcategory": "badlex",
     "question_text": "What exception does this code throw?",
     "code": "program...",
     "option_a": "LexException",
     "option_b": "ParseException",
     "option_c": "SemanticAnalysisException",
     "option_d": "ExecutionException",
     "option_e": "No exception",
     "correct_answer": "A",
     "explanation": "Detailed explanation here...",
     "difficulty": "medium"
   }
   ```
3. Restart the bot to load new questions

### Adding New Handlers

1. Create new file in `bot/handlers/`
2. Create a router: `router = Router()`
3. Add handlers with decorators
4. Register in `bot/main.py`: `dp.include_router(your_handler.router)`

## Performance Tips

- The bot uses SQLite by default (lightweight, no setup)
- For production with many users, consider PostgreSQL
- Redis is used for session storage (included in docker-compose)
- Questions are loaded once at startup (fast responses)

## Security

- Never commit `.env` file with real bot token
- Use environment variables for sensitive data
- Bot token in `.env` is kept private
- User data is stored locally in SQLite database

## License

Created for CSCI 501 Final Exam Preparation
Free to use for educational purposes

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f bot`
2. Review this guide
3. Contact your instructor or TA
