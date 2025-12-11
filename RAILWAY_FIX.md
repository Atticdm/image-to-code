# 🔧 Исправление ошибок деплоя на Railway

## Проблема

Railway не может найти Dockerfile в корне проекта, потому что:
1. Backend находится в поддиректории `backend/`
2. Frontend находится в поддиректории `frontend/`
3. Railway ищет Dockerfile в корне по умолчанию

## Решение

### Вариант 1: Создать отдельные сервисы (рекомендуется)

1. **Backend сервис:**
   - Root Directory: `backend`
   - Dockerfile Path: `Dockerfile`

2. **Frontend сервис:**
   - Root Directory: `frontend`
   - Dockerfile Path: `Dockerfile.prod`

### Вариант 2: Использовать railway.toml в корне

Railway автоматически обнаружит `railway.toml` в корне проекта, но для этого нужно указать правильный путь к Dockerfile.

## Настройка в Railway Dashboard

### Backend:
1. Settings → Source
2. Root Directory: `backend`
3. Settings → Build
4. Dockerfile Path: `Dockerfile`

### Frontend:
1. Settings → Source
2. Root Directory: `frontend`
3. Settings → Build
4. Dockerfile Path: `Dockerfile.prod`

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

