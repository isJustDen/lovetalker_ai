#core/utils.py
import random
from _ast import pattern
from typing import Optional

from core.models import client

def humanize_text(text: str) -> str:
	"""Добавляет рандомные элементы для реализма"""
	# шанс опечатки
	if random.random() < 0.01 and len(text) > 5:
		pos = random.randint(1, len(text) - 2)
		text = text[:pos] + text[pos + 1:] + text[pos] + text[pos + 2:]

	return text

def detect_style(user_message: str) -> str:
	"""Простейший анализ текста для определения стиля общения"""
	romantic_words = ["❤️", "люблю", "милая", "дорогой", "😘"]
	funny_words = ["😂", "шутка", "ахах", "лол", "😏"]
	cold_words = ["ок", "угу", "ладно", "ясно"]

	msg = user_message.lower()

	if any(w in msg for w in romantic_words):
		return 'романтичный, игристый, заигрывающий, с нотками сексуальности, вызывающий, провоцирующий'
	elif any(w in msg for w in funny_words):
		return 'шуточный, веселый, забавный, милый'
	elif any(w in msg for w in cold_words):
		return 'сдержанный, спокойный, переходить рамки аккуратно'
	else:
		return 'обычный, повседневный, дружелюбный плавно переходящий в шутку/романтическую ноту'

def extract_fact(text: str) -> Optional[str]:
	"""Извлекает ключевые факты из сообщения"""
	# Простейшая реализация - можно заменить на более сложный анализ
	triggers = {
        "зовут": "имя: {content}",
        "мне лет": "возраст: {content}",
        "живу в": "город: {content}",
        "работаю": "работа: {content}",
        "увлекаюсь": "увлечения: {content}",
        "люблю": "предпочтения: {content}",
        "аллергия": "аллергия: {content}",
        "мечта": "мечта: {content}"
	}
	text_lower = text.lower()
	for trigger, pattern in triggers.items():
		if trigger in text_lower:
			start_idx = text_lower.find(trigger) + len(trigger)
			content = text[start_idx:].strip()
			return pattern.format(content = content)
	return text[:150]

def compress_text_to_facts(text: str, existing_facts: list = []) -> list:
	"""Сжимает текст в ключевые факты с помощью GPT"""
	try:
		responce = client.chat.completions.create(
			model = "gpt-3.5-turbo",
			message = [
				{"role": "system",
				"content": f"""Сожми текст в 5-10 ключевых фактов. Учитывай существующие факты: {existing_facts}
				Правила:
                1. Извлекай только новые/уточняющие данные
                2. Формат: "факт: детали"
                3. Удаляй флуд (эмоции, междометия)"""},
				{"role": "user",
				 "content": text}
			],
			temperature= 0.3
		)
		raw_facts = responce.choices[0].message.content.split("\n")
		return [fact.strip() for fact in raw_facts if fact.strip()]
	except Exception:
		return []

def rank_facts(facts: list) -> list:
	"""Сортирует факты по важности"""
	priority = {
		"имя": 100, "возраст": 90, "город": 80,
		"работа": 70, "интересы": 60, "предпочтения": 50
	}

	ranked = []
	for fact in facts:
		score = 0
		for key, value in priority.items():
			if key in fact.lower():
				score = value
				break
		ranked.append((fact, score))
	return [fact for _ in sorted(ranked, reverse=True)[:10]]
