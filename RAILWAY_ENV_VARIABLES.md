# 🔧 Переменные окружения для Railway

## 📋 Backend Сервис (`image-to-code`)

### ⚠️ Обязательные переменные:

```bash
# API ключи для AI моделей (нужен хотя бы один)
OPENAI_API_KEY=sk-...                    # Для GPT-4o, GPT-4.1
ANTHROPIC_API_KEY=sk-ant-...             # Для Claude 4.5 Sonnet, Claude Opus
```

### 📝 Опциональные переменные:

```bash
# Дополнительные AI модели
GEMINI_API_KEY=...                       # Для Gemini 2.0 (опционально)

# Генерация изображений
REPLICATE_API_KEY=...                    # Для Flux Schnell, DALL-E 3 (опционально)

# Кастомный OpenAI API endpoint
OPENAI_BASE_URL=https://...              # Если используете прокси OpenAI API (опционально)

# Production флаги
IS_PROD=True                              # Установите True для production (опционально)

# Отладка (только для разработки)
MOCK=False                                # True для тестирования без реальных API вызовов
IS_DEBUG_ENABLED=False                    # Включить debug логи
DEBUG_DIR=/path/to/debug                  # Директория для debug файлов
```

### 🔄 Автоматические переменные Railway:

```bash
PORT=7001                                 # Railway устанавливает автоматически
RAILWAY_ENVIRONMENT=production            # Устанавливается Railway
RAILWAY_PROJECT_ID=...                    # Устанавливается Railway
```

---

## 🎨 Frontend Сервис (`image-to-codefront` или ваш frontend сервис)

### ⚠️ Обязательные переменные:

```bash
# URL бэкенда (замените на ваш реальный URL бэкенда)
VITE_HTTP_BACKEND_URL=https://image-to-code-production.up.railway.app
VITE_WS_BACKEND_URL=wss://image-to-code-production.up.railway.app

# Флаг деплоя
VITE_IS_DEPLOYED=true                    # Должно быть именно "true" (строка)
```

### 📝 Опциональные переменные:

```bash
# Секрет для форм (если используете)
VITE_PICO_BACKEND_FORM_SECRET=...        # Опционально
```

### 🔄 Автоматические переменные Railway:

```bash
PORT=8080                                 # Railway устанавливает автоматически
RAILWAY_ENVIRONMENT=production            # Устанавливается Railway
```

---

## 📍 Где настроить в Railway:

### Для Backend:

1. Откройте Railway Dashboard: https://railway.app/project/ff479365-a5ed-45ff-9afc-e38d711e7fbc
2. Выберите сервис **`image-to-code`** (Backend)
3. Перейдите в **Settings → Variables**
4. Добавьте переменные из списка выше

### Для Frontend:

1. В том же проекте выберите ваш **Frontend сервис**
2. Перейдите в **Settings → Variables**
3. Добавьте переменные из списка выше

---

## ✅ Минимальная конфигурация для работы:

### Backend (минимум):
```bash
OPENAI_API_KEY=sk-...
# ИЛИ
ANTHROPIC_API_KEY=sk-ant-...
```

### Frontend (минимум):
```bash
VITE_HTTP_BACKEND_URL=https://image-to-code-production.up.railway.app
VITE_WS_BACKEND_URL=wss://image-to-code-production.up.railway.app
VITE_IS_DEPLOYED=true
```

---

## 🔍 Как узнать URL бэкенда:

1. Откройте Backend сервис в Railway Dashboard
2. Перейдите в **Settings → Networking**
3. Скопируйте **Public Domain** (например: `image-to-code-production.up.railway.app`)
4. Используйте его для фронтенда:
   - `VITE_HTTP_BACKEND_URL=https://image-to-code-production.up.railway.app`
   - `VITE_WS_BACKEND_URL=wss://image-to-code-production.up.railway.app`

---

## ⚠️ Важные замечания:

1. **HTTPS/WSS**: Используйте `https://` и `wss://` для production (не `http://` или `ws://`)
2. **VITE_IS_DEPLOYED**: Должно быть строкой `"true"`, не булевым значением
3. **API ключи**: Храните в секретах Railway, не коммитьте в git
4. **PORT**: Railway устанавливает автоматически, обычно не нужно задавать вручную

---

## 🧪 Проверка переменных:

После настройки проверьте логи:
```bash
# Backend логи
railway logs --service image-to-code

# Frontend логи  
railway logs --service image-to-codefront
```

Если видите ошибки подключения - проверьте URL бэкенда в переменных фронтенда.

