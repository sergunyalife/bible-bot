#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime
import nest_asyncio
import os

# Разрешаем вложенные event loops
nest_asyncio.apply()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация - используем переменные окружения
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8517108220:AAFVjFuHe6_EEVP7jKGhDrnAVM-ajQAWF0s")
EXCEL_FILE_PATH = os.path.join(os.path.dirname(__file__), "Test.xlsx")

# URL изображения стиха дня
DAILY_VERSE_IMAGE_URL = "https://imageproxy.youversionapi.com/640x640/https://s3.amazonaws.com/static-youversionapi-com/images/base/103172/1280x1280.jpg"

# Глобальные переменные
bible_data = None
user_translations = {}

async def load_bible_data():
    """Загрузка данных из Excel файла"""
    global bible_data
    try:
        df = pd.read_excel(EXCEL_FILE_PATH, sheet_name='Sheet1')
        df.columns = ['Day', 'Book_RU', 'Chapter', 'Verses', 'Book_EN', 'SYNO', 'NRP']
        df['Day'] = df['Day'].ffill().astype(int)
        bible_data = df
        logger.info(f"Данные загружены успешно. Всего записей: {len(df)}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {e}")
        return False

# ... ВСТАВЬТЕ ВСЕ ВАШИ ФУНКЦИИ ЗДЕСЬ ...
# (start, button_handler, show_main_menu, send_daily_reading, send_reading_by_day, 
# show_day_selection, show_translation_selection, set_user_translation, show_about, error_handler)

async def main_polling():
    """Запуск в режиме polling (для разработки)"""
    # Загружаем данные
    if not await load_bible_data():
        print("❌ Не удалось загрузить данные из Excel файла!")
        return

    print("✅ Данные успешно загружены")
    print(f"✅ Всего дней: {len(bible_data['Day'].unique())}")
    print(f"✅ Всего записей: {len(bible_data)}")

    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error_handler)

    print("🤖 Telegram бот запущен в режиме polling...")
    
    # Запускаем polling
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    asyncio.run(main_polling())