# Startup Exchange

Прототип модуля стартапов и вакансий для тестового задания AI-native разработчика.

## Запуск

1. Создайте в существующем PostgreSQL отдельную базу `startup_exchange` и пользователя с правами только на эту базу. Это можно сделать повторяемым скриптом:

   ```bash
   POSTGRES_ADMIN_URL='postgresql://admin:ADMIN_PASSWORD@127.0.0.1:5432/postgres' \
   APP_DB_PASSWORD='LONG_RANDOM_APP_PASSWORD' \
   ./scripts/provision_postgres.sh
   ```

   При необходимости задайте `APP_DB` и `APP_DB_USER`. Скрипт можно запускать повторно: он создаёт отсутствующие объекты и обновляет пароль прикладной роли. Если PostgreSQL работает на том же сервере вне Docker, разрешите подключения от Docker-сети и используйте `host.docker.internal` в `DATABASE_URL`.
2. Скопируйте `.env.example` в `.env` и укажите `DATABASE_URL`, секреты, публичный `DOMAIN` и `CORS_ORIGINS`.
3. Направьте DNS-запись `DOMAIN` на сервер и откройте TCP-порты 80 и 443.
4. Выполните `docker compose up --build -d`. Caddy автоматически получит и продлит TLS-сертификат Let's Encrypt для публичного домена.
5. Откройте приложение на `https://<DOMAIN>`. Для демонстрационных аккаунтов выполните `docker compose exec backend python -m scripts.seed`.

Аккаунты seed: `founder@example.com` и `builder@example.com`, пароль для обоих — `password123`.

## Возможности

- вход под разными пользователями и JWT-защита API;
- лента опубликованных стартапов и вакансий;
- создание публикации с описанием и полем «кого ищет автор»;
- отправка отклика с защитой от повторной отправки;
- принятие или отклонение отклика только автором публикации;
- адаптивный интерфейс для телефона и desktop;
- пустые состояния, ошибки и уведомление о результате действия.

## Backend

Доменные сущности `User`, `Post` и `Response` хранятся в PostgreSQL. Для локальных тестов используется SQLite. Уникальное ограничение `(post_id, applicant_id)` делает повторную отправку отклика безопасной на уровне базы данных.

Основные маршруты: `POST /api/auth/login`, `POST /api/auth/telegram`, `POST /api/telegram/webhook`, `GET /api/posts`, `POST /api/posts`, `GET /api/posts/{id}`, `POST /api/posts/{id}/responses`, `GET /api/responses/sent`, `GET /api/responses/received`, `PATCH /api/responses/{id}`.

## Telegram Mini App

1. Создайте бота через `@BotFather` и положите токен в `TELEGRAM_BOT_TOKEN`.
2. Разверните frontend по публичному HTTPS-адресу и задайте `VITE_API_URL`.
3. Настройте кнопку меню вручную в BotFather или выполните `TELEGRAM_APP_URL=https://your-domain.example python -m scripts.configure_telegram`.
4. Для команд бота задайте `TELEGRAM_WEBHOOK_SECRET` и установите webhook на `https://your-api.example/api/telegram/webhook`, передав тот же секрет в параметре `secret_token` метода `setWebhook`.
5. Открытие приложения через Telegram автоматически вызывает `/api/auth/telegram`; backend проверяет подпись `initData` и создаёт JWT-сессию.

Токен бота хранится только в backend-окружении. Frontend получает только Telegram SDK и URL API.

## Проверки

```bash
python -m compileall app scripts tests
pytest -q
docker compose config
```

Frontend собирается в Node.js builder-слое Docker-образа и отдаётся Caddy из статических файлов; локальный npm-клиент не требуется. Caddy проксирует `/api` и `/health` во внутренний backend и автоматически обслуживает HTTPS.

Схема базы управляется Alembic: backend-контейнер выполняет `alembic upgrade head` перед запуском API.

## Решения и допущения

Telegram WebApp SDK подключён, а Telegram ID сохраняется в профиле пользователя. Для локального запуска остаётся тестовый email/password-вход. Реальные платежи, загрузка файлов, Redis и Kafka не входят в обязательный объём.

## Использование ИИ

ИИ применялся для чернового проектирования слоёв, API и UI. Сгенерированные решения проверялись вручную: отдельно проверены запрет отклика на собственную публикацию, уникальность отклика, проверка владельца при принятии решения и отсутствие секретов в репозитории. В README намеренно зафиксированы именно эти проверки, а не непроверенные утверждения.

Фактически потраченное время: около 4 часов, включая проектирование, backend, frontend, тесты и документацию.

Локально подтверждены `pytest` (2 теста), `compileall`, `alembic upgrade head` на SQLite и `docker compose config`. Полный Docker smoke-check отложен, поскольку Docker Desktop Engine недоступен в текущей среде; frontend production build требует npm или работающего Docker Engine.

Полный план находится в [PLAN.md](PLAN.md).
