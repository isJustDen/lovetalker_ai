#main.py
import asyncio

from aiogram.filters import Command
from aiogram import Bot, Dispatcher, types

from config import BOT_TOKEN
from core.user_db import register_user, get_user, init_db

# создаём экземпляр бота

bot = Bot(token = BOT_TOKEN)
dp = Dispatcher()

# обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
	# регистрируем пользователя в БД
	register_user(message.from_user.id, message.from_user.first_name)

	await message.answer("Привет 👋 Я Lovetalker AI 💬. Ты зарегистрирован. Готов начать знакомство!")


# Информация о пользователе профиля
@dp.message(Command("profile"))
async def profile_command(message: types.Message):
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


# функция запуска бота
async def main():
	init_db()
	print("Бот запущен...")
	await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
	asyncio.run(main())