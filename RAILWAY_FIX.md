# 🔧 Исправление ошибок деплоя на Railway

## ✅ Исправлено!

Проблема была в том, что Railway не мог найти Dockerfile, потому что:
1. Backend находится в поддиректории `backend/`
2. Frontend находится в поддиректории `frontend/`
3. Railway ищет Dockerfile в корне по умолчанию

## Решение

Созданы отдельные `railway.toml` файлы для каждого сервиса:

### Backend (`backend/railway.toml`):
- Dockerfile Path: `Dockerfile` (относительно `backend/`)
- Start Command: `poetry run uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend (`frontend/railway.toml`):
- Dockerfile Path: `Dockerfile.prod` (относительно `frontend/`)
- Использует nginx для статики

## Настройка в Railway Dashboard

### Для Backend сервиса:
1. Settings → Source
2. Root Directory: `backend` ⚠️ **ВАЖНО!**
3. Settings → Build
4. Dockerfile Path: `Dockerfile` (или оставить пустым, railway.toml укажет)

### Для Frontend сервиса (если создадите отдельный):
1. Settings → Source
2. Root Directory: `frontend` ⚠️ **ВАЖНО!**
3. Settings → Build
4. Dockerfile Path: `Dockerfile.prod` (или оставить пустым, railway.toml укажет)

## Переменные окружения

### Backend:
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PORT=7001
```

### Frontend:
```
VITE_HTTP_BACKEND_URL=https://your-backend.railway.app
VITE_WS_BACKEND_URL=wss://your-backend.railway.app
VITE_IS_DEPLOYED=true
PORT=80
```

## Проверка

После настройки проверьте:
1. Build логи - должны показывать успешную сборку
2. Deploy логи - должны показывать запуск приложения
3. URL сервисов - должны быть доступны

