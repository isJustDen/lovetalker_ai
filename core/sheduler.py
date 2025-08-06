#core/scheduler.py
import asyncio

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
	await asyncio.sleep(delay)
	await bot.send_message(chat_id, text)

