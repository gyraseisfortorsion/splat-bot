#!/bin/bash

# SPLAT Exam Bot - Quick Start Script

echo "🎓 SPLAT Exam Bot - Quick Start"
echo "================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "✅ .env file created!"
    echo ""
    echo "🔧 Please edit .env and add your BOT_TOKEN:"
    echo "   nano .env"
    echo ""
    echo "Get your bot token from @BotFather on Telegram:"
    echo "   1. Open Telegram and search for @BotFather"
    echo "   2. Send /newbot and follow instructions"
    echo "   3. Copy the token and paste it in .env"
    echo ""
    read -p "Press Enter when you've added your BOT_TOKEN..."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "🐳 Starting Docker containers..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 5

echo ""
echo "📊 Checking bot status..."
docker-compose ps

echo ""
echo "✅ Bot is running!"
echo ""
echo "📝 Next steps:"
echo "   1. Open Telegram and search for your bot"
echo "   2. Send /start to begin"
echo "   3. Start practicing for your exam!"
echo ""
echo "📋 Useful commands:"
echo "   docker-compose logs -f bot    # View bot logs"
echo "   docker-compose ps              # Check status"
echo "   docker-compose down            # Stop bot"
echo "   docker-compose restart bot     # Restart bot"
echo ""
echo "🚀 Good luck with your exam!"
