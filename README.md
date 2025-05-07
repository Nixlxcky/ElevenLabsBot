# CensureWords
## 🇷🇺 Русский

Telegram бот на базе aiogram и ElevenLabs API, который может озвучивать текст b позволяет копировать голос.

### 🔹 Возможности

* ✍️ Доступны все языки озвучки.
* 🔄 С помощью комнады sync_voices синхронизирует языки с вашего ElevenLabs профиля, генерируя клавиатуры и добавляя их в базу данных.
* ✅ Удобный интерфейс


### 🧰 Технологии

`Python3.13`, `Aiogram3.+`, `MySQL`, `aiohttp`, `sqlalchemy` 

### 🚀 Установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/Nixlxcky/ElevenLabsBot.git
cd ElevenLabsBot
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` со следующими переменными:

```
BOT_TOKEN=<ключ бота>
ELEVENLABS_API_KEY=<ключ ElevenLabs> 
DATABASE_URL =<ссылка MySQL>
```

4. Запустите бот:

```bash
python main.py
```


## 🇬🇧 English

A Telegram bot based on aiogram and ElevenLabs API that can voice text and allows you to copy the voice.

### 🔹 Features

* ✍️ All voice languages ​​are available.
* 🔄 Using the sync_voices command, it synchronizes languages ​​from your ElevenLabs profile, generating keyboards and adding them to the database.
* ✅ User-friendly interface

### 🧰 Technologies

`Python3.13`, `Aiogram3.+`, `MySQL`, `aiohttp`, `sqlalchemy`

### 🚀 Installation

1. Clone the repository:

```bash
git clone https://github.com/Nixlxcky/ElevenLabsBot.git
cd ElevenLabsBot
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with the following variables:

```
BOT_TOKEN=<bot key>
ELEVENLABS_API_KEY=<ElevenLabs key>
DATABASE_URL =<MySQL URL>
```

4. Run the bot:

```bash
python main.py
```

