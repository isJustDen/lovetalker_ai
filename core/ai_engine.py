#core/ai_engine.py
import datetime
from typing import Dict, List
from openai import OpenAI
from config import OPENAI_API_KEY
from core.user_db import get_user, get_partner_style

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_reply(history: List[Dict[str, str]], user_message: str, user_id: int = None, partner:str=None) -> str:
	"""Генерация ответа GPT с учётом предпочтений"""
	style_prompt = get_style_prompt(user_id) if user_id else ""
	partner_prompt = get_partner_style(user_id, partner) if partner else "дружелюбно"
	time_prompt = get_time_prompt()
	messages = [
		{
			"role": "system",
			"content": (
				"Ты - Lovetalker AI 💬, остроумный, человекоподобный, кокетливый чат-бот по имени Денис. "
				"Отвечай естественно и дружелюбно. Будь креативным. Не говори, что ты ИИ или бот, веди себя как человек. "
				"Поддерживай беседу и задавай уточняющие вопросы, оставляй о себе хорошее впечатление, старайся понравиться, учитывай контекст."
				f"Стиль: {style_prompt}. Текущее время {time_prompt}. Общайся в стиле: {partner_prompt}"
			)
		}
	]

	# Добавляем историю диалога
	messages.extend(history[-10:])  # Берем последние 10 сообщений

	# Добавляем новое сообщение пользователя
	messages.append({"role": "user", "content": user_message})

	try:
		response = client.chat.completions.create(
			model="gpt-3.5-turbo",
			messages=messages,
			max_tokens=256,
			temperature=0.7,
			top_p=0.9,
			frequency_penalty=0.5,
			presence_penalty=0.5
		)
		return response.choices[0].message.content.strip()
	except Exception as e:
		return f"⚠️ Произошла ошибка: {str(e)}"

def get_style_prompt(user_id: int) -> str:
	"""Формируем стиль общения на основе лайков/дизлайков"""
	user = get_user(user_id)
	if not user:
		return "Будь дружелюбен и креативным"

	name = user[1] if len (user) > 1 else "Пользователь"
	likes = user[2] if len(user) > 2 else 0
	dislikes = user[3] if len(user) > 3 else 0

	if likes > dislikes:
		return "Будь энергичным, кокетливым, используй юмор и смайлы."
	elif dislikes > likes:
		return "Будь спокойным, уважительным, избегай слишком дерзких фраз."
	else:
		return "Будь дружелюбным и лёгким в общении."

def get_time_prompt() -> str:
	hour = datetime.datetime.now().hour

	if 7 <= hour < 12:
		return 'Сейчас утро, будь бодрым и позитивным ☀️'
	elif 12 <= hour < 18:
		return "Сейчас день, будь энергичным и дружелюбным 🌼."
	elif 18 <= hour < 23:
		return "Сейчас вечер, будь уютным и кокетливым 🌙."
	else:
		return "Поздняя ночь, будь спокойным, тёплым и расслабленным 🌌."

