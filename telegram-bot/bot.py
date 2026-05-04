import asyncio
import logging
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Настройки
API_TOKEN = '8660009405:AAH2IqzAMmI6uy0fCA-JLuuf-a6swR_nzmw'
CHANNEL_USERNAME = '@Lydka_Kornycod'
CHANNEL_ID = -1003885416281

# Настройка логирования
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Словарь для отслеживания времени последнего ответа пользователю (чтобы не спамить)
last_reply = {}


@dp.message()
async def handle_new_members(message: types.Message):
    """Приветствие когда кто-то вступает в группу"""

    # Проверяем что это наша группа
    if message.chat.id != CHANNEL_ID and message.chat.username != CHANNEL_USERNAME.replace('@', ''):
        return

    # Проверяем есть ли новые участники в сообщении
    if message.new_chat_members:
        for user in message.new_chat_members:
            # Не приветствуем ботов
            if user.is_bot:
                continue

            username = user.username or f"user_{user.id}"
            first_name = user.first_name or "игрок"

            print(f"✅ НОВЫЙ УЧАСТНИК: @{username}")

            # Разные приветствия
            welcomes = [
                f"👋 Добро пожаловать в группу, {first_name}! 🎰",
                f"✨ Привет, {first_name}! Крути 🎰 и выигрывай!",
                f"🎉 {first_name} присоединился к нам! Желаем удачи! 🍀",
                f"🤝 Рады видеть тебя, {first_name}! Играй и побеждай!",
                f"⭐️ Новый игрок: {first_name}! Твоя удача ждет!",
                f"🔥 {first_name} в игре! Крути 🎰 и забирай NFT!",
                f"💫 Поприветствуем {first_name}! Пусть фортуна улыбнется!"
            ]

            welcome_text = random.choice(welcomes)

            # Добавляем правила
            welcome_text += (
                "\n\n🎰 **Правила игры:**\n"
                "7️⃣7️⃣7️⃣ – NFT до 20.000 ⭐️\n"
                "🍋🍋🍋 – 🚀 или 💐\n"
                "🍇🍇🍇 – 💝 или 🧸\n"
                "🥂🥂🥂 – 💝 или 🧸\n\n"
                "⭐️ Дешевые звёзды - @Kornycod"
            )

            # Отправляем приветствие
            try:
                await bot.send_message(
                    chat_id=message.chat.id,
                    text=welcome_text,
                    parse_mode='Markdown'
                )
                logging.info(f"✅ Приветствие для @{username}")
            except Exception as e:
                logging.error(f"❌ Ошибка приветствия: {e}")


async def periodic_message():
    """Отправляет сообщение каждые 90 минут"""

    message_text = (
        "Хочешь NFT? Крути 🎰\n\n"
        "7️⃣7️⃣7️⃣ – NFT до 20.000 ⭐️\n"
        "🍋🍋🍋 – 🚀 или 💐\n"
        "🍇🍇🍇 – 💝 или 🧸\n"
        "🥂🥂🥂 – 💝 или 🧸\n\n"
        "САМЫЕ дешевые звёзды с любым способом оплаты ⭐️ - @Kornycod"
    )

    while True:
        try:
            current_time = datetime.now().strftime("%H:%M")
            current_date = datetime.now().strftime("%d.%m.%Y")

            # Пробуем отправить через USERNAME
            try:
                await bot.send_message(
                    chat_id=CHANNEL_USERNAME,
                    text=f"⏰ {current_date} | {current_time}\n\n{message_text}"
                )
                logging.info(f"✅ Отправлено в {CHANNEL_USERNAME} в {current_time}")
            except:
                # Если не получилось - через ID
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=f"⏰ {current_date} | {current_time}\n\n{message_text}"
                )
                logging.info(f"✅ Отправлено через ID: {CHANNEL_ID} в {current_time}")

        except Exception as e:
            logging.error(f"❌ Ошибка: {e}")

        await asyncio.sleep(5400)  # 90 минут


@dp.message()
async def handle_slot_machine(message: types.Message):
    """Обрабатывает сообщения с эмодзи 🎰"""

    # Игнорируем команды
    if message.text and message.text.startswith('/'):
        return

    # Игнорируем сообщения от самого бота
    if message.from_user.is_bot:
        return

    # Проверяем наличие 🎰 в тексте
    if message.text and '🎰' in message.text:
        user_id = message.from_user.id
        username = message.from_user.username or f"user_{user_id}"
        current_time = datetime.now()

        # Проверяем, не отвечали ли пользователю в последние 30 минут
        if user_id in last_reply:
            time_diff = current_time - last_reply[user_id]
            if time_diff < timedelta(minutes=30):
                logging.info(f"⏸ Пропускаем @{username} (прошло только {time_diff.seconds // 60} мин)")
                return

        # Случайный процент увеличения шанса (от 5% до 15%)
        increase = random.randint(5, 15)

        # Случайные вариации ответов
        replies = [
            f"🎰 @{username}, твой шанс увеличился на {increase}%! Крути дальше!",
            f"✨ @{username}, удача ближе! Шанс +{increase}%!",
            f"🔥 @{username}, твой потенциал вырос на {increase}%! Ещё немного!",
            f"💫 @{username}, теперь твой шанс выше на {increase}%!",
            f"⭐️ @{username}, удача поворачивается к тебе! +{increase}%",
            f"🎯 @{username}, ты ближе к выигрышу! Шанс +{increase}%",
            f"🚀 @{username}, твой шанс взлетел на {increase}%!",
            f"🌈 @{username}, фортуна улыбается! +{increase}% к успеху!"
        ]

        reply_text = random.choice(replies)

        # Отвечаем с задержкой 1-3 секунды (как живой человек)
        await asyncio.sleep(random.uniform(1, 3))

        try:
            await message.reply(reply_text)
            last_reply[user_id] = current_time
            logging.info(f"✅ Ответили @{username} (+{increase}%) на сообщение: {message.text[:50]}")
        except Exception as e:
            logging.error(f"❌ Не удалось ответить @{username}: {e}")


@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer(
        f"🤖 **Бот запущен!**\n\n"
        f"📢 **Канал:** {CHANNEL_USERNAME}\n"
        f"⏱ **Отправка:** каждые 90 минут\n"
        f"👋 **Приветствие:** новых участников\n"
        f"🎰 **Фишка:** когда кто-то пишет 🎰 в чат, бот отвечает про увеличение шанса\n\n"
        f"**Сообщение:**\n"
        f"7️⃣7️⃣7️⃣ – NFT до 20.000 ⭐️\n"
        f"🍋🍋🍋 – 🚀 или 💐\n"
        f"🍇🍇🍇 – 💝 или 🧸\n"
        f"🥂🥂🥂 – 💝 или 🧸\n\n"
        f"Команды:\n"
        f"/stop - остановить автоотправку\n"
        f"/status - статус"
    )

    if not hasattr(dp, 'sending_task'):
        dp.sending_task = asyncio.create_task(periodic_message())
        await message.answer("✅ **Автоотправка запущена! (каждые 90 минут)**")


@dp.message(Command('stop'))
async def cmd_stop(message: types.Message):
    if hasattr(dp, 'sending_task'):
        dp.sending_task.cancel()
        delattr(dp, 'sending_task')
        await message.answer("⏹ **Автоотправка остановлена**")
    else:
        await message.answer("❌ **Автоотправка не запущена**")


@dp.message(Command('status'))
async def cmd_status(message: types.Message):
    status_text = "✅ АКТИВЕН" if hasattr(dp, 'sending_task') else "⏸ ОСТАНОВЛЕН"

    # Статистика ответов за последний час
    active_users = len([u for u, t in last_reply.items() if datetime.now() - t < timedelta(hours=1)])

    await message.answer(
        f"📊 **СТАТУС БОТА**\n\n"
        f"🤖 **Автоотправка:** {status_text}\n"
        f"📢 **Канал:** {CHANNEL_USERNAME}\n"
        f"⏱ **Интервал:** 90 минут\n"
        f"👋 **Приветствие:** ВКЛ\n"
        f"🎰 **Режим:** Ответы на 🎰\n"
        f"👥 **Активных за час:** {active_users}\n"
        f"💬 **Всего ответов:** {len(last_reply)}"
    )


async def main():
    print("=" * 50)
    print("🤖 БОТ ЗАПУЩЕН!")
    print("=" * 50)
    print(f"📢 Канал: {CHANNEL_USERNAME}")
    print(f"⏱ Отправка каждые 90 минут")
    print(f"👋 Приветствие: новых участников")
    print(f"🎰 Режим: ответы на сообщения с 🎰")
    print("=" * 50)

    # Автоматический запуск
    dp.sending_task = asyncio.create_task(periodic_message())
    print("🚀 Автоотправка ЗАПУЩЕНА!\n")

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹ Бот остановлен")