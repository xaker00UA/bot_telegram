
### Для запуска бота требуется
1. Создать .env file
``` env
TOKEN=Telegram_bot_token
API_KEY=api_key_token
ADMIN_ID=id_telegram_account
```
Получить апи ключ можно [тут](https://www.mindee.com/)
2. Выполнить команду
``` bash
docker build -t telegram_bot .
docker run -d --name my_telegram_bot telegram_bot
```