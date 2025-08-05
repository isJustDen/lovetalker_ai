#core/ai_engine.py

from typing import Dict, List
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_reply(history: List[Dict[str, str]], user_message: str) -> str:
	"""Генерирует ответ с помощью GPT-3.5-turbo (Chat Completions API)"""

	messages = [
		{
			"role": "system",
			"content": (
				"Ты - Lovetalker AI 💬, остроумный, человекоподобный, кокетливый чат-бот по имени Денис. "
				"Отвечай естественно и дружелюбно. Будь креативным. Не говори, что ты ИИ или бот. "
				"Поддерживай беседу и задавай уточняющие вопросы."
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