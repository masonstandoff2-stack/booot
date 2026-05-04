import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

BOT_TOKEN = "8652350653:AAGnivt_JB8vtHnLRmgg7m65qeKaOZ9G35E"          
OWNER_ID = 8733257796                   

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Команда /start для пользователей
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот-помощник.\n"
        "Напиши мне свой вопрос, и я передам его владельцу.\n"
        "Ответ придёт сюда же."
    )

# Пересылка ЛЮБОГО сообщения от пользователя -> владельцу
@dp.message()
async def forward_to_owner(message: types.Message):
    user = message.from_user
    user_link = f"<a href='tg://user?id={user.id}'>{user.full_name}</a>"
    
    # Формируем подпись: от кого пришло сообщение
    caption_info = f"✉️ Вопрос от {user_link} (ID: {user.id})"

    try:
        # Пробуем переслать оригинальное сообщение владельцу с добавлением подписи
        if message.text:
            await bot.send_message(
                OWNER_ID,
                f"{caption_info}\n\n📝 Текст:\n{message.text}"
            )
        elif message.photo:
            # Для фото – отправляем фото с подписью
            photo = message.photo[-1].file_id
            await bot.send_photo(
                OWNER_ID,
                photo,
                caption=f"{caption_info}\n\n📸 Фото"
            )
        elif message.voice:
            await bot.send_voice(
                OWNER_ID,
                message.voice.file_id,
                caption=f"{caption_info}\n\n🎤 Голосовое"
            )
        else:
            # Остальные типы (видео, документы, стикеры и т.д.) – пересылаем как есть
            await bot.copy_message(OWNER_ID, message.chat.id, message.message_id)
            await bot.send_message(
                OWNER_ID,
                f"{caption_info}\n(переслано как копия)"
            )
        
        # Подтверждение пользователю
        await message.answer("✅ Ваше сообщение отправлено владельцу. Ожидайте ответа.")
    
    except Exception as e:
        logging.error(f"Ошибка при пересылке: {e}")
        await message.answer("❌ Не удалось отправить сообщение. Попробуйте позже.")

# ОТВЕТ ВЛАДЕЛЬЦА ПОЛЬЗОВАТЕЛЮ
# Владелец пишет боту: /reply 123456789 Привет, вот ответ
@dp.message(Command("reply"))
async def reply_to_user(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("⛔ У вас нет прав на эту команду.")
        return
    
    # Разбираем команду: /reply user_id текст ответа
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer(
            "❌ Формат: /reply <ID_пользователя> <текст ответа>\n"
            "Пример: /reply 123456789 Здравствуйте, вот решение вашей проблемы."
        )
        return
    
    _, user_id_str, reply_text = parts
    try:
        user_id = int(user_id_str)
    except ValueError:
        await message.answer("❌ ID пользователя должен быть числом.")
        return
    
    try:
        await bot.send_message(
            user_id,
            f"📬 Ответ от владельца:\n\n{reply_text}"
        )
        await message.answer(f"✅ Ответ отправлен пользователю {user_id}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
