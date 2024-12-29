import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio
import threading


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

vacancies_cache = []
is_parsing = False


def no_attributes(tag):
    return tag.name == 'div' and not tag.attrs


def fetch_jobs(max_pages=5):
    url = 'https://hh.ru/search/vacancy'

    params = {
        'area': 113,  
        'only_with_salary': True,
        'L_save_area': True,
        'search_field': 'name',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    vacancies = []

    for page in range(max_pages):
        params['page'] = page

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html5lib')
        main_content = soup.find(id="a11y-main-content")
        job_cards = main_content.find_all(no_attributes)

        for card in job_cards:
            all_spans = card.find_all('span')
            if len(all_spans) > 10:
                vacancies.append({
                    'title': all_spans[2].get_text(strip=True),
                    'description': f'{all_spans[7].get_text(strip=True)} / {all_spans[6].get_text(strip=True)} / {all_spans[10].get_text(strip=True)}'
                })
    return vacancies


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот для поиска вакансий. Используйте /help для получения списка команд.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Приветствие\n"
        "/help - Справка по командам\n"
        "/fetch - Запустить парсер и получить вакансии\n"
        "/view - Просмотреть кэшированные вакансии\n"
    )


async def fetch_jobs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_parsing
    if is_parsing:
        await update.message.reply_text("Парсер уже запущен, подождите завершения.")
        return

    is_parsing = True
    await update.message.reply_text("Запуск парсинга вакансий...")

    loop = asyncio.get_running_loop()
    thread = threading.Thread(target=perform_parsing, args=(loop, update, context))
    thread.start()


def perform_parsing(loop, update, context):
    global vacancies_cache, is_parsing
    vacancies_cache = fetch_jobs(max_pages=1)
    is_parsing = False

    message = f"Найдено {len(vacancies_cache)} вакансий."
    asyncio.run_coroutine_threadsafe(
        context.bot.send_message(chat_id=update.effective_chat.id, text=message), 
        loop
    )


async def view_vacancies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not vacancies_cache:
        await update.message.reply_text("Нет кэшированных вакансий. Запустите парсинг.")
        return

    response = ""
    for vac in vacancies_cache:
        response += f"{vac['title']}\n{vac['description']}\n\n"

    await update.message.reply_text(response or "Нет вакансий.")
    

def main():
    # add token
    telegram_token = ''
    application = ApplicationBuilder().token(telegram_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("fetch", fetch_jobs_command))
    application.add_handler(CommandHandler("view", view_vacancies))
    application.run_polling()
     

if __name__ == "__main__":
    main()