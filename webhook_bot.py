#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from datetime import datetime
import os
from flask import Flask, request

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_BOT_TOKEN = "8517108220:AAFVjFuHe6_EEVP7jKGhDrnAVM-ajQAWF0s"
EXCEL_FILE_PATH = os.path.join(os.path.dirname(__file__), "Test.xlsx")

# URL для вебхука на PythonAnywhere
WEBHOOK_URL = "https://sergunyalife.pythonanywhere.com/webhook"
# или для тестирования:
# WEBHOOK_URL = "https://sergunyalife.pythonanywhere.com/webhook" + TELEGRAM_BOT_TOKEN

# Глобальные переменные
bible_data = None
user_translations = {}  # Словарь для хранения выбора перевода пользователями

# ========== ВАШИ ФУНКЦИИ БОТА (без изменений) ==========
# Копируйте ВСЕ ваши функции сюда (load_bible_data, start, button_handler и т.д.)
# ... [вставьте все ваши функции из оригинального кода] ...

def load_bible_data_sync():
    """Синхронная загрузка данных (для Flask)"""
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

# ========== FLASK ПРИЛОЖЕНИЕ ==========
app = Flask(__name__)

# Инициализация бота при старте
application = None

@app.route('/')
def index():
    return '🤖 Бот для чтения Библии работает!<br><a href="/setwebhook">Установить вебхук</a>'

@app.route('/setwebhook')
def set_webhook():
    global application
    try:
        if application is None:
            # Инициализируем бота
            application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
            
            # Добавляем обработчики
            application.add_handler(CommandHandler("start", start))
            application.add_handler(CallbackQueryHandler(button_handler))
            application.add_error_handler(error_handler)
            
            # Загружаем данные
            load_bible_data_sync()
        
        # Устанавливаем вебхук
        webhook_info = application.bot.set_webhook(WEBHOOK_URL)
        return f'✅ Вебхук установлен!<br>{webhook_info}'
    except Exception as e:
        return f'❌ Ошибка: {e}'

@app.route('/webhook', methods=['POST'])
async def webhook():
    global application
    if application is None:
        return 'Bot not initialized', 500
    
    try:
        # Получаем обновление от Telegram
        update = Update.de_json(await request.get_json(), application.bot)
        
        # Обрабатываем обновление
        await application.process_update(update)
        return 'ok', 200
    except Exception as e:
        logger.error(f"Ошибка обработки вебхука: {e}")
        return 'error', 500

if __name__ == '__main__':
    # Загружаем данные при старте
    load_bible_data_sync()
    
    # Запускаем Flask
    app.run(host='0.0.0.0', port=8080)