#main.py

import asyncio

#from aiogram.types import ChatActions
import asyncio
import random
import sqlite3

from aiogram.filters import Command
from aiogram import Bot, Dispatcher, types


from config import BOT_TOKEN
from core.sheduler import init_scheduler, schedule_message, schedule_reminder
from core.user_db import register_user, get_user, init_db, add_like, add_dislike, save_message, get_dialogs, set_mode, \
	get_mode, get_connection, get_partners, add_partner
from core.ai_engine import generate_reply
from core.utils import humanize_text

# создаём экземпляр бота
bot = Bot(token = BOT_TOKEN)
dp = Dispatcher()
#------------------------------------------------------------------------------------------------------------------

# обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
	"""регистрируем пользователя в БД"""
	register_user(message.from_user.id, message.from_user.first_name)

	await message.answer("Привет 👋 Я Lovetalker AI 💬. Ты зарегистрирован. Готов начать знакомство!")


# обработчик команды /profile
@dp.message(Command("profile"))
async def profile_command(message: types.Message):
	"""Информация о пользователе профиля"""
	user = get_user(message.from_user.id)

	if user:
		user_id, name, likes, dislikes = user
		await message.answer(
			f"📊 Профиль: {name}\n"
			f"👍 Лайков: {likes}\n"
			f"👎 Дизлайков: {dislikes}"
		)
	else:
		await message.answer("Ты еще не зарегистрирован, нажми /start")


# обработчик команды /like
@dp.message(Command("like"))
async def like_command(message: types.Message):
	"""Фукнция постановки лайка(запись)"""
	add_like(message.from_user.id)
	await message.answer("👍 Лайк добавлен")

	user = get_user(message.from_user.id)
	await message.answer(f"Теперь у тебя {user[2]} лайков и {user[3]} дизлайков.")


# обработчик команды /dislike
@dp.message(Command("dislike"))
async def dislike_command(message: types.Message):
	"""Фукнция постановки дизлайка(запись)"""
	add_dislike(message.from_user.id)
	await message.answer('👎 Дизлайк добавлен!')

	user = get_user(message.from_user.id)
	await message.answer(f"Теперь у тебя {user[2]} лайков и {user[3]} дизлайков.")


# обработчик команды /chat
@dp.message(Command("chat"))
async def chat_command(message: types.Message):
	#имитируем диалог с кандидатами
	args = message.text.split(maxsplit=1)
	if len(args) < 2:
		await message.answer("❗ Используй: /chat <имя собеседника>")
		return

	partner = args[1].strip()
	save_message(message.from_user.id, partner,'system',f"Начал чат с {partner}")
	await message.answer(f"📩 Диалог  с {partner} начат! Пиши сообщения.")

	# бот напомнит через какое-то время часов
	schedule_reminder(bot, message.chat.id, "Как твои делишки, как настроение?")



# обработчик команды /history
@dp.message(Command("history"))
async def history_command(message: types.Message):
	"""История сообщений"""
	args = message.text.split(maxsplit=1)
	if len(args) < 2:
		partners = get_partners(message.from_user.id)
		if partners:
			await message.answer("❗ Укажи имя собеседника. Доступные диалоги:\n" + "\n".join(partners))
		else:
			await message.answer("❗ У тебя пока нет диалогов. Начни новый с /chat <имя>")
		return

	partner = args[1].strip()

	# Проверяем существование диалога
	conn = get_connection()
	cur = conn.cursor()
	cur.execute("""
	SELECT 1 FROM dialogs
	WHERE user_id = ? AND partner_name = ?
	LIMIT 1
	""", (message.from_user.id, partner))
	exists = cur.fetchone() is not None
	conn.close()

	if not exists:
		await message.answer(f"Диалог с {partner} еще не начинался. Используй /chat {partner}")
		return


	dialog = get_dialogs(message.from_user.id, partner, limit = 10)

	if dialog:
		text = f"📝 История с {partner}:\n"
		for sender, msg, time in dialog:
			text += f"[{time}] {sender}: {msg}\n"
		await message.answer(text)
	else:
		await message.answer(f"История с {partner} пуста.")


# обработчик команды /mode
@dp.message(Command("mode"))
async def mode_command(message: types.Message):
	"""Выбор режима общения"""
	keyboard = types.InlineKeyboardMarkup(
		inline_keyboard=[
			[types.InlineKeyboardButton(text="Assist 📝", callback_data = "mode_assist"),
			 types.InlineKeyboardButton(text = "Semi-auto ⚡", callback_data = "mode_semi")],
			[types.InlineKeyboardButton(text="Auto 🤖", callback_data = "mode_auto")
			 ]
		]
	)
	await message.answer('Выбери режим общения:', reply_markup=keyboard)


@dp.callback_query(lambda c: c.data.startswith("mode_"))
async def process_mode_callback(callback: types.CallbackQuery):
	mode_mapping = {
		"mode_assist": "assist",
        "mode_semi": "semi-auto",
        "mode_auto": "auto"
	}
	mode = mode_mapping[callback.data]
	set_mode(callback.from_user.id, mode)
	await callback.message.answer(f"✅ Режим общения изменён на: {mode}")
	await callback.answer()


@dp.message(Command('partner'))
async def partner_command(message: types.Message):
	args = message.text.split(maxsplit=2)
	if len(args) < 3:
		await message.answer("❗ Используй: /partner <имя> <стиль>")
		return

	name, style = args[1], args[2]
	add_partner(message.from_user.id, name, style)
	await message.answer(f"✅ Добавлен партнёр {name} со стилем: {style}")













# ловим любое другое сообщение
@dp.message()
async def handle_message(message: types.Message):
	"""Захватчик всех сообщений с чата"""


	# Определяем партнера - берем последнего из истории
	conn = get_connection()
	cur = conn.cursor()
	cur.execute("""
	SELECT partner_name FROM dialogs
	WHERE user_id = ?
	ORDER BY timestamp DESC
	LIMIT 1
	""", (message.from_user.id,))
	last_partner = cur.fetchone()
	partner = last_partner[0] if last_partner else "bot"


	# Сохраняем сообщение пользователя
	save_message(message.from_user.id, partner, 'user', message.text)
	# получаем режим пользователя
	mode = get_mode(message.from_user.id)

	# получаем историю для контекста
	dialog_history = get_dialogs(message.from_user.id, partner, limit = 10)
	# берём историю (последние 10 сообщений)
	history = [
		{"role": "user" if sender == "user" else "assistant", "content": msg}
		for sender, msg, _ in dialog_history
	]

	if mode == "assist":
		# GPT предлагает несколько вариантов
		reply1 = generate_reply(history, message.text + " (вариант 1)", user_id=message.from_user.id)
		reply2 = generate_reply(history, message.text + " (вариант 2)", user_id=message.from_user.id)
		reply3 = generate_reply(history, message.text + " (вариант 3)", user_id=message.from_user.id)
		await message.answer(f"✍️ Варианты ответа:\n")
		await message.answer(f"1️⃣ {reply1}\n")
		await message.answer(f"2️⃣ {reply2}\n")
		await message.answer(f"3️⃣ {reply3}")

	elif mode == "semi-auto":
		# GPT отвечает, но можно поправить
		reply = generate_reply(history, message.text, user_id=message.from_user.id)
		save_message(message.from_user.id, partner,"bot", reply)
		await message.answer(f"⚡ Ответ: {reply}\n\n(Можешь переписать вручную)")

	elif mode == "auto":
		# Полный автопилот
		reply = humanize_text(generate_reply(history, message.text, user_id=message.from_user.id))
		save_message(message.from_user.id, partner,"bot", reply)

		delay = random.randint(120, 300)
		schedule_message(bot, message.chat.id, f"{reply}", delay=delay)

		await bot.send_chat_action(message.chat.id, "typing")	# статус "печатает..."
		await asyncio.sleep(random.uniform(2, 59.0))

		await message.answer(f"🤖 {reply}")


#------------------------------------------------------------------------------------------------------------------
# функция запуска бота
async def main():
	init_db()
	init_scheduler()

	# Тестовая проверка БД
	conn = sqlite3.connect('data/users.db')
	cur = conn.cursor()
	cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
	print(f"Таблицы в БД: {cur.fetchall()}")
	conn.close()


	print("Бот запущен...")
	await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
	asyncio.run(main())