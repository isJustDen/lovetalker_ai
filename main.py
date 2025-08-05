#main.py

import asyncio

from aiogram.filters import Command
from aiogram import Bot, Dispatcher, types

from config import BOT_TOKEN
from core.user_db import register_user, get_user, init_db, add_like, add_dislike, save_message, get_dialogs
from core.ai_engine import generate_reply
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
	#имитируем диалог с самим ботом (позже будет с кандидатами)
	save_message(message.from_user.id, 'user', "Начал чат с ботом")
	await message.answer("📩 Диалог начат! Пиши сообщения, я их сохраню.")


# обработчик команды /history
@dp.message(Command("history"))
async def history_command(message: types.Message):
	"""История сообщений"""
	dialog = get_dialogs(message.from_user.id, limit = 5)

	if dialog:
		text = "📝 Последние сообщения:\n"
		for sender, msg, time in dialog:
			text += f"[{time}] {sender}: {msg}\n"
		await message.answer(text)
	else:
		await message.answer("История пуста")


# ловим любое другое сообщение
@dp.message()
async def handle_message(message: types.Message):
	"""Захватчик всех сообщений с чата"""

	dialog_history = get_dialogs(message.from_user.id, limit = 5)
	# берём историю (последние 5 сообщений)
	history = [
		{"role": "user" if sender == "user" else "assistant", "content": msg}
		for sender, msg, _ in dialog_history
	]

	# генерируем обращение пользователя
	save_message(message.from_user.id, 'user', message.text)

	# генерируем ответ GPT 	и сохраняем ответ бота
	reply = generate_reply(history, message.text)
	save_message(message.from_user.id, 'bot', reply)

	await message.answer(reply)


#------------------------------------------------------------------------------------------------------------------
# функция запуска бота
async def main():
	init_db()
	print("Бот запущен...")
	await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
	asyncio.run(main())