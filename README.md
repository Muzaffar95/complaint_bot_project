# ComplaintBot Project

## 📦 Описание
Telegram-бот для приёма жалоб и админ-панель на FastAPI.  
Хранит данные в PostgreSQL, генерирует PDF, экспортирует Excel.  
Развёртывание через Docker Compose + SSL на nginx.

---

## 🚀 Развёртывание

### 1. Клонирование или копирование архива

```bash
git clone https://github.com/your-org/complaint_bot_project.git
cd complaint_bot_project
```

### 2. Настрой .env

Создай `.env` файл на основе `.env.example`:

```bash
cp .env.example .env
nano .env
```

Укажи:

- `TELEGRAM_BOT_TOKEN=your_telegram_bot_token`
- `WEBHOOK_URL=https://yourdomain.com/webhook`
- `POSTGRES_*` — доступ к базе

### 3. Запуск через Docker Compose

```bash
docker-compose up --build -d
```

---

## 🌐 Доступ

- Бот: `@your_bot` → /start
- Панель: `https://yourdomain.com/html?token=...`
- Получение токена:

```bash
curl -X POST https://yourdomain.com/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"
```

---

## 🛠 Nginx + SSL

Файл: `/etc/nginx/sites-available/yourdomain.com`

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    location /webhook {
        proxy_pass http://localhost:8000;
    }

    location / {
        proxy_pass http://localhost:8001;
    }

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
}
```

---

## 🧰 Полезные команды

- Проверить логи:

```bash
docker-compose logs bot
```

- Перезапуск:

```bash
docker-compose restart bot
```

- Удалить всё:

```bash
docker-compose down --volumes
```

---

## ✅ Готово!

Система работает, Telegram-бот принимает жалобы, админ-панель доступна, всё в контейнерах.

Разработал: 🧑‍💻 Muzaffar Abdulxamitov
