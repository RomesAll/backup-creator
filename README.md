## Программа для создания backup файлов на Linux

Feature:
 - сохранения метаданных о файлах, папок
 - в версии v1.2.0 добавлена многопроцессорность
 - метаданные сохраняются в Mongodb на локальном сервере

Запуск в терминале в корне проекта:
```
docker compose up -d
[путь к .venv с установленными зависимостями] src/main.py backup [путь к ресурсу, /home/user/target] [путь в место сохранения, /home/user/backup]
```

Для работы программы нужно добавить .env файл в корень проекта по шаблону:
```
MONGODB__USERNAME=root
MONGODB__PASSWORD=example
MONGODB__HOST=127.0.0.1
MONGODB__PORT=27017
MONGODB__EXPRESS_URL=mongodb://root:example@mongo:27017/
MONGODB__BASICAUTH_ENABLED=true
MONGODB__BASICAUTH_USERNAME=mongoexpressuser
MONGODB__BASICAUTH_PASSWORD=mongoexpresspass
LOGGING__LEVEL=INFO
LOGGING__NAME_APP_LOGGER=app
```

Зависимости:
```
annotated-types==0.7.0
dnspython==2.8.0
fire==0.7.1
pydantic==2.13.4
pydantic-settings==2.14.2
pydantic_core==2.46.4
pymongo==4.17.0
pymongo-amplidata==3.6.0.post1
python-dotenv==1.2.2
ruff==0.15.22
termcolor==3.3.0
typing-inspection==0.4.2
typing_extensions==4.16.0
```
