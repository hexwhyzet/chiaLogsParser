import telebot

from config import Config
from logs_parser import get_logs_paths, does_this_log_filepath_exists, LogsData, all_days_stats_telegram_format

config = Config()

bot = telebot.TeleBot(config["telegram_bot_token"], parse_mode=None)


@bot.message_handler(commands=['start', 'help'])
def support(message):
    bot.send_message(message.chat.id, "List all available log files: /list\nNumber of plotted blocks per day: /stats")


def generate_receptions_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    for shortened_path, full_path in get_logs_paths():
        markup.row(telebot.types.InlineKeyboardButton(shortened_path, callback_data=full_path))
    return markup


@bot.message_handler(commands=['list'])
def list_logs_files(message):
    bot.send_message(message.chat.id, "Select log files you would like to observe",
                     reply_markup=generate_receptions_markup())


@bot.message_handler(commands=['stats'])
def stats(message):
    bot.send_message(message.chat.id, "Number of plots created:\n" + all_days_stats_telegram_format())


@bot.callback_query_handler(func=lambda query: does_this_log_filepath_exists(query.data))
def send_stats(query):
    bot.send_message(
        query.message.json['chat']['id'],
        "```\n" + f"{query.data}:\n" + LogsData(query.data).telegram_format() + "\n```",
        parse_mode='MarkdownV2',
    )


if __name__ == '__main__':
    bot.polling(interval=config["polling_interval"])
