import os
import logging
from dotenv import load_dotenv
from telegram import Update, constants
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Загружаем переменные из .env
load_dotenv()

BOT_TOKEN = os.getenv("8652350653:AAGnivt_JB8vtHnLRmgg7m65qeKaOZ9G35E")
OWNER_ID = int(os.getenv("8733257796"))

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# ---------- КОМАНДА /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение для пользователя"""
    await update.message.reply_text(
        "👋 Привет! Я бот-посредник.\n\n"
        "📝 Напиши мне свой вопрос, и я передам его владельцу.\n"
        "✅ Ответ придёт сюда же, как только владелец ответит.\n\n"
        "⚠️ Пожалуйста, будьте вежливы и описывайте проблему чётко."
    )


# ---------- ПЕРЕСЫЛКА СООБЩЕНИЙ ВЛАДЕЛЬЦУ ----------
async def forward_to_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пересылает любое сообщение от пользователя владельцу"""
    user = update.effective_user
    message = update.message
    
    # Формируем информацию о пользователе
    user_info = (
        f"👤 <b>Новый вопрос!</b>\n"
        f"📛 Имя: {user.full_name}\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"🔗 Ссылка: tg://user?id={user.id}\n"
        f"📅 Username: @{user.username if user.username else 'нет'}\n"
        f"{'─' * 30}\n"
    )
    
    try:
        # Отправляем владельцу информацию о пользователе + пересылаем сообщение
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=user_info,
            parse_mode="HTML",
        )
        
        # Пересылаем оригинальное сообщение
        await message.copy(chat_id=OWNER_ID)
        
        # Подтверждение пользователю
        await message.reply_text(
            "✅ Ваше сообщение доставлено владельцу!\n\n"
            "⏳ Ожидайте ответа. Как только ответят — вы получите уведомление."
        )
        
        logger.info(f"Переслано сообщение от {user.id} ({user.full_name}) владельцу")
        
    except Exception as e:
        logger.error(f"Ошибка при пересылке: {e}")
        await message.reply_text(
            "❌ Произошла ошибка при отправке. Попробуйте позже."
        )


# ---------- ОТВЕТ ВЛАДЕЛЬЦА ПОЛЬЗОВАТЕЛЮ ----------
async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для владельца: /reply ID текст ответа"""
    
    # Проверяем, что команду даёт владелец
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("⛔ У вас нет прав для использования этой команды.")
        return
    
    # Разбираем команду: /reply 123456789 Привет, вот ответ
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "❌ <b>Неверный формат!</b>\n\n"
            "Использование:\n"
            "<code>/reply ID_пользователя текст ответа</code>\n\n"
            "Пример:\n"
            "<code>/reply 123456789 Здравствуйте, мы уже решаем ваш вопрос</code>",
            parse_mode="HTML",
        )
        return
    
    user_id_str = args[0]
    reply_text = " ".join(args[1:])
    
    # Проверяем, что ID - число
    if not user_id_str.isdigit():
        await update.message.reply_text("❌ ID пользователя должен быть числом!")
        return
    
    user_id = int(user_id_str)
    
    try:
        # Отправляем ответ пользователю
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📬 <b>Ответ от владельца:</b>\n\n{reply_text}\n\n"
                 f"💡 Если у вас остались вопросы — напишите снова.",
            parse_mode="HTML",
        )
        
        # Подтверждение владельцу
        await update.message.reply_text(
            f"✅ <b>Ответ успешно отправлен!</b>\n\n"
            f"👤 Пользователь ID: <code>{user_id}</code>\n"
            f"💬 Текст ответа: {reply_text}",
            parse_mode="HTML",
        )
        
        logger.info(f"Ответ отправлен пользователю {user_id}")
        
    except Exception as e:
        logger.error(f"Ошибка при отправке ответа пользователю {user_id}: {e}")
        await update.message.reply_text(
            f"❌ <b>Ошибка!</b>\n\n"
            f"Не удалось отправить сообщение пользователю {user_id}.\n"
            f"Возможно, пользователь заблокировал бота.\n\n"
            f"Текст ошибки: {e}",
            parse_mode="HTML",
        )


# ---------- ОТПРАВКА КОПИИ СЕБЕ (для тестов) ----------
async def send_copy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для владельца: отправить копию сообщения себе (для тестов пересылки)"""
    if update.effective_user.id != OWNER_ID:
        return
    
    if update.message.reply_to_message:
        await update.message.reply_to_message.copy(chat_id=OWNER_ID)
        await update.message.reply_text("✅ Копия отправлена")
    else:
        await update.message.reply_text("❌ Ответьте на сообщение, которое хотите скопировать")


# ---------- ОБРАБОТЧИК ОШИБОК ----------
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Логирование ошибок"""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Уведомляем владельца об ошибке
    if update and update.effective_user:
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"⚠️ Произошла ошибка при обработке сообщения от {update.effective_user.id}\n"
                 f"Ошибка: {context.error}"
        )


# ---------- ГЛАВНАЯ ФУНКЦИЯ ЗАПУСКА ----------
def main():
    """Запуск бота"""
    # Создаём приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reply", reply_to_user))
    application.add_handler(CommandHandler("copy", send_copy))  # полезно для тестов
    
    # Пересылаем ВСЕ сообщения (кроме команд) владельцу
    # Исключаем команды, чтобы не пересылать /reply и /start
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND | 
            filters.PHOTO | 
            filters.VOICE | 
            filters.VIDEO |
            filters.Document.ALL |
            filters.Sticker.ALL,
            forward_to_owner
        )
    )
    
    # Регистрируем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    print("🤖 Бот запущен и готов к работе!")
    print(f"👑 Владелец ID: {OWNER_ID}")
    print("📨 Все сообщения от пользователей будут пересылаться вам")
    print("💬 Для ответа используйте: /reply ID_пользователя текст")
    print("⏹️ Для остановки нажмите Ctrl+C\n")
    
    application.run_polling()


if __name__ == "__main__":
    main()
