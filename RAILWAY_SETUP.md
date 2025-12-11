# 🚂 Настройка Railway для Image-to-Code

## ✅ Что исправлено

1. ✅ Создан `backend/railway.toml` с правильным путем к Dockerfile
2. ✅ Создан `frontend/railway.toml` для будущего frontend сервиса
3. ✅ Обновлен корневой `railway.toml` для backend
4. ✅ Исправлены Dockerfile для правильной работы с переменной PORT
5. ✅ Исправлен `nginx.conf.template` для подстановки PORT

## ⚠️ ВАЖНО: Настройка в Railway Dashboard

### Для текущего сервиса "image-to-code" (Backend):

1. Откройте Railway Dashboard: https://railway.app/project/ff479365-a5ed-45ff-9afc-e38d711e7fbc
2. Выберите сервис `image-to-code`
3. Перейдите в **Settings → Source**
4. Установите **Root Directory**: `backend` ⚠️ **КРИТИЧЕСКИ ВАЖНО!**
5. Сохраните изменения

### Переменные окружения (Settings → Variables):

Добавьте следующие переменные:

```
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
PORT=7001
```

## 🔄 После настройки

После установки Root Directory Railway автоматически:
1. Найдет `backend/railway.toml`
2. Использует `backend/Dockerfile` для сборки
3. Запустит backend на порту из переменной PORT

## 📝 Создание Frontend сервиса (опционально)

Если хотите деплоить frontend отдельно:

1. В Railway Dashboard создайте новый сервис
2. Settings → Source → Root Directory: `frontend`
3. Settings → Build → Dockerfile Path: `Dockerfile.prod`
4. Добавьте переменные:
   ```
   VITE_HTTP_BACKEND_URL=https://image-to-code-production.up.railway.app
   VITE_WS_BACKEND_URL=wss://image-to-code-production.up.railway.app
   VITE_IS_DEPLOYED=true
   PORT=80
   ```

## 🐛 Проверка логов

После деплоя проверьте логи:
```bash
railway logs --build
railway logs --deploy
```

Если видите ошибку "couldn't locate the dockerfile" - проверьте Root Directory в Settings!

