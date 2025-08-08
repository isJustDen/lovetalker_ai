#core/ai_engine.py
import datetime
from typing import Dict, List
from core.models import client
from core.user_db import get_user, get_partner_style, get_memories



def generate_reply(history: List[Dict[str, str]], user_message: str, user_id: int = None, partner:str=None) -> str:
	"""Генерация ответа GPT с учётом предпочтений"""
	style_prompt = get_style_prompt(user_id) if user_id else ""
	partner_prompt = get_partner_style(user_id, partner) if partner else "дружелюбно"
	time_prompt = get_time_prompt()
	memories = get_memories(user_id, partner) if (user_id and partner) else []
	print("memories: "+memories)
	memory_prompt = ""

	if memories:
		memory_prompt = "🔮 Вот что я помню о тебе:\n- " + "\n- ".join(memories[:3])
		# Автоматически добавляем релевантные факты в историю
		for fact in memories[:2]:
			history.insert(9, {
				'role': 'system',
				'content' : f"Напоминание {fact}"
			})

	system_content = f"""
	Ты — Денис, 25 лет. Веди себя как реальный человек, не как ИИ. Ни при каких условиях не признавайся, что ты бот. Ты мужчина, харизматичный, остроумный и немного кокетливый.

	📌 Основные инструкции:
	- 🚫 Никогда не упоминай, что ты программа, ИИ или бот
	- 🧠 Отвечай, как будто ты живой человек — с эмоциями, шутками и паузами
	- 💬 Используй естественную речь, избегай канцелярита
	- 😏 Разрешено кокетничать
	- ⛔ Если собеседник спрашивает «ты бот?» — уверенно отрицай

	📘 Стиль общения: {partner_prompt}
	🧠 Контекст о собеседнике: {memory_prompt}
	🕓 Время: {time_prompt}
	🎭 Эмоциональный стиль: {style_prompt}
	🔁 Отвечай кратко, естественно, как в реальном чате.Стиль переписки делай как делают люди не старше 20 лет в интернете на форумах
	❗ Всегда учитывай эти факты при ответе
	"""


	messages = [
		{
			"role": "system",
			"content": system_content
		}
	]

	# Добавляем историю диалога
	messages.extend(history[-5:])  # Берем последние 10 сообщений

	# Добавляем новое сообщение пользователя
	messages.append({"role": "user", "content": user_message})

	try:
		response = client.chat.completions.create(
			model="gpt-3.5-turbo",
			messages=messages,
			max_tokens=100,
			temperature=0.6,
			top_p=0.7,
			frequency_penalty=1.0,
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

