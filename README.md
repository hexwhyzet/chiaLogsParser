<h1 align="center">Welcome to Chia Logs Parser 👋</h1>

## Description

This project is created for monitoring logs on remote plotting machine via Telegram.
Functionality is still meager, but it will probably expand.

## Config

Before we start you should create **config.json** by coping **config_template.json** file and filling all fields like that.

```json
{
  "telegram_bot_token": "Telegram bot token from BotFather",
  "polling_interval": 5,
  "logs_directories": [
    "user1/dir1/dir2",
    "user2/dir4"
  ]
}
```

## Install

```sh
git clone https://github.com/hexwhyzet/chiaLogsParser
cd chiaLogsParser
python3 -m venv ./
. ./bin/activate
pip install -r requirements.txt
```

## Usage

```sh
screen -S chiaLogsParser
. ./bin/activate
python telegram.py
```

## Author
👤 **Vanya Kabakov**

## License
Copyright © 2021 [Ivan Kabakov](https://github.com/hexwhyzet).
This project is [MIT](https://github.com/hexwhyzet/chiaLogsParser/blob/master/LICENSE) licensed.