#!/bin/bash

echo "🔍 Проверка готовности системы для Image-to-Code..."
echo ""

# Проверка Python
echo "📦 Python:"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "  ✅ $PYTHON_VERSION"
else
    echo "  ❌ Python не установлен"
fi

# Проверка Poetry
echo ""
echo "📦 Poetry:"
if command -v poetry &> /dev/null; then
    POETRY_VERSION=$(poetry --version)
    echo "  ✅ $POETRY_VERSION"
else
    echo "  ❌ Poetry не установлен (установите: pip install --upgrade poetry)"
fi

# Проверка Node.js
echo ""
echo "📦 Node.js:"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "  ✅ $NODE_VERSION"
else
    echo "  ❌ Node.js не установлен"
fi

# Проверка Yarn
echo ""
echo "📦 Yarn:"
if command -v yarn &> /dev/null; then
    YARN_VERSION=$(yarn --version)
    echo "  ✅ Yarn $YARN_VERSION"
else
    echo "  ⚠️  Yarn не установлен (можно использовать npm)"
fi

# Проверка npm
echo ""
echo "📦 npm:"
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "  ✅ npm $NPM_VERSION"
else
    echo "  ❌ npm не установлен"
fi

# Проверка Docker
echo ""
echo "📦 Docker:"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo "  ✅ $DOCKER_VERSION"
else
    echo "  ⚠️  Docker не установлен (опционально)"
fi

# Проверка .env файла в backend
echo ""
echo "📝 Конфигурация:"
if [ -f "backend/.env" ]; then
    echo "  ✅ backend/.env существует"
    if grep -q "OPENAI_API_KEY" backend/.env || grep -q "ANTHROPIC_API_KEY" backend/.env; then
        echo "  ✅ API ключи найдены в .env"
    else
        echo "  ⚠️  API ключи не найдены в .env"
    fi
else
    echo "  ⚠️  backend/.env не найден (создайте файл с API ключами)"
fi

# Проверка зависимостей backend
echo ""
echo "📚 Зависимости Backend:"
if [ -d "backend/.venv" ] || [ -f "backend/poetry.lock" ]; then
    echo "  ✅ Зависимости могут быть установлены"
else
    echo "  ⚠️  Зависимости не установлены (запустите: cd backend && poetry install)"
fi

# Проверка зависимостей frontend
echo ""
echo "📚 Зависимости Frontend:"
if [ -d "frontend/node_modules" ]; then
    echo "  ✅ node_modules существует"
else
    echo "  ⚠️  node_modules не найден (запустите: cd frontend && yarn install)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Проверка завершена!"
echo ""
echo "📖 Подробные инструкции: ИНСТРУКЦИЯ_ПО_РАЗВЕРТЫВАНИЮ.md"
echo ""

