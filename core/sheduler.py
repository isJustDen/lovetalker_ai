#core/scheduler.py
import asyncio
import random
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler


scheduler = AsyncIOScheduler()

def init_scheduler():
	scheduler.start()

def schedule_message(bot, chat_id: int, text: str, delay: int = 60):
	"""Запланировать отправку сообщения через delay секунд"""
	scheduler.add_job(
		send_delayed_message,
		trigger='date',
		run_date = None,
		args=[bot, chat_id, text],
		misfire_grace_time=30,
		next_run_time=None,
		kwargs={'delay': delay}
	)


async def send_delayed_message(bot, chat_id:int, text: str, delay: int=60):
	"""Отправляет сообщения ен сразу, а с задержкой(как реальный человек)"""
	await asyncio.sleep(delay)
	await bot.send_message(chat_id, text)

def schedule_reminder(bot, chat_id:int, text: str):
	"""Отправляет одно напоминание в случайное время (от 5 до 16 часов с текущего момента)"""
	random_hours = random.randint(3, 12)
	run_time = datetime.now() + timedelta(hours=random_hours)

	scheduler.add_job(
		send_delayed_message,
		trigger='date',
		run_date = run_time,
		args=[bot, chat_id, text]
	)

