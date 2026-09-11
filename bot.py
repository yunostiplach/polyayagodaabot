import logging
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from time_descriptions import time_meanings


# ============================================================
# НАСТРОЙКИ
# ============================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


minutes_by_hour = {
    "00": ["00", "11", "22", "33", "44", "55"],
    "01": ["01", "10", "11", "21"],
    "02": ["02", "20", "21", "22"],
    "03": ["03", "13", "30", "31", "33"],
    "04": ["04", "14", "40", "41", "44"],
    "05": ["05", "15", "50", "51", "55"],
    "06": ["06", "16"],
    "07": ["07", "17"],
    "08": ["08", "18"],
    "09": ["09", "19"],
    "10": ["00", "01", "10", "11"],
    "11": ["00", "01", "10", "11", "22", "33", "44", "55"],
    "12": ["12", "21", "22", "33"],
    "13": ["13", "31", "33"],
    "14": ["14", "41", "44"],
    "15": ["15", "51", "55"],
    "16": ["16"],
    "17": ["17"],
    "18": ["18"],
    "19": ["19"],
    "20": ["00", "02", "20", "22"],
    "21": ["01", "12", "21", "22"],
    "22": ["00", "02", "20", "22", "33", "44", "55"],
    "23": ["23", "32", "33"],
}


SPHERES = {
    "love": ("❤️", "Любовь", "любовь"),
    "money": ("💰", "Деньги", "деньги"),
    "work": ("💼", "Работа и карьера", "работа"),
    "state": ("🌿", "Состояние", "состояние"),
    "general": ("✨", "Общее", "общее"),
}


def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🕐 Время на часах", callback_data="time_menu")],
        [InlineKeyboardButton("✨ Астрология", callback_data="astro")],
        [InlineKeyboardButton("🔮 Таро", callback_data="taro")],
        [InlineKeyboardButton("💜 Тёплое послание", callback_data="heartfelt")],
    ])


def back_to_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Привет, это бот Поли Ягоды 🤳🏻\n\n"
        "Здесь ты можешь получать ответы через:\n"
        "🕐 значения времени на часах\n"
        "✨ астрологию\n"
        "🔮 Таро\n"
        "💜 тёплые послания\n\n"
        "Выбери раздел ниже:",
        reply_markup=main_keyboard(),
    )


async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "✨ Выбери раздел:",
        reply_markup=main_keyboard(),
    )


async def time_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()

    keyboard = []

    row = []
    for hour in range(24):
        row.append(
            InlineKeyboardButton(
                f"{hour:02d}",
                callback_data=f"hour_{hour:02d}",
            )
        )

        if len(row) == 6:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
    ])

    text = (
        "🕐 Выбери час, который ты видишь на часах:\n\n"
        "После этого я покажу только те варианты минут, "
        "которые входят в твою библиотеку времени."
    )

    if query:
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


async def show_minutes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    hour = query.data.split("_", 1)[1]
    minutes_list = minutes_by_hour.get(hour, [])

    keyboard = []
    row = []

    for minute in minutes_list:
        row.append(
            InlineKeyboardButton(
                f"{hour}:{minute}",
                callback_data=f"minute_{hour}:{minute}",
            )
        )

        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("◀️ Назад к часам", callback_data="time_menu")
    ])
    keyboard.append([
        InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
    ])

    await query.edit_message_text(
        f"🕐 Ты выбрала час {hour}.\n\n"
        f"Выбери время:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_spheres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    time_key = query.data.split("_", 1)[1]
    context.user_data["selected_time"] = time_key

    keyboard = [
        [InlineKeyboardButton("❤️ Любовь", callback_data=f"sphere_love_{time_key}")],
        [InlineKeyboardButton("💰 Деньги", callback_data=f"sphere_money_{time_key}")],
        [InlineKeyboardButton("💼 Работа и карьера", callback_data=f"sphere_work_{time_key}")],
        [InlineKeyboardButton("🌿 Состояние", callback_data=f"sphere_state_{time_key}")],
        [InlineKeyboardButton("✨ Общее", callback_data=f"sphere_general_{time_key}")],
        [InlineKeyboardButton("◀️ Назад к времени", callback_data=f"hour_{time_key[:2]}")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")],
    ]

    await query.edit_message_text(
        f"🕰 Ты увидела {time_key}\n\n"
        "В какой сфере хочешь узнать значение?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_time_meaning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, sphere_type, time_key = query.data.split("_", 2)

    sphere_info = SPHERES.get(sphere_type)
    if sphere_info is None:
        sphere_info = SPHERES["general"]

    emoji, sphere_name, sphere_key = sphere_info

    time_data = time_meanings.get(time_key, {})
    description = time_data.get(
        sphere_key,
        "✨ Для этого времени и сферы описание пока не добавлено.",
    )

    keyboard = [
        [InlineKeyboardButton("◀️ Выбрать другую сферу", callback_data=f"minute_{time_key}")],
        [InlineKeyboardButton("🕐 Выбрать другое время", callback_data="time_menu")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")],
    ]

    await query.edit_message_text(
        f"🕰 {time_key}\n"
        f"{emoji} {sphere_name}\n\n"
        f"{description}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def astro_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "✨ Раздел астрологии пока в разработке.",
        reply_markup=back_to_main_keyboard(),
    )


async def taro_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "🔮 Раздел Таро пока в разработке.",
        reply_markup=back_to_main_keyboard(),
    )


async def heartfelt_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "💜 Раздел тёплых посланий пока в разработке.",
        reply_markup=back_to_main_keyboard(),
    )


def main():
    token = os.getenv("BOT_TOKEN")

    if not token:
        raise RuntimeError(
            "Не найден BOT_TOKEN. "
            "Задай токен бота в переменной окружения BOT_TOKEN."
        )

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("time", time_menu))

    application.add_handler(CallbackQueryHandler(show_minutes, pattern=r"^hour_"))
    application.add_handler(CallbackQueryHandler(show_spheres, pattern=r"^minute_"))
    application.add_handler(CallbackQueryHandler(show_time_meaning, pattern=r"^sphere_"))
    application.add_handler(CallbackQueryHandler(time_menu, pattern=r"^time_menu$"))
    application.add_handler(CallbackQueryHandler(astro_menu, pattern=r"^astro$"))
    application.add_handler(CallbackQueryHandler(taro_menu, pattern=r"^taro$"))
    application.add_handler(CallbackQueryHandler(heartfelt_message, pattern=r"^heartfelt$"))
    application.add_handler(CallbackQueryHandler(back_to_main, pattern=r"^back_to_main$"))

    print("✨ Бот Поли Ягоды запущен!")
    application.run_polling()


if __name__ == "__main__":
    main()