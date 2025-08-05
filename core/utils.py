#core/utils.py
import random

emojis = ["😉", "😊", "🔥", "😂", "❤️", "😏"]

def humanize_text(text: str) -> str:
	"""Добавляет рандомные элементы для реализма"""
	# шанс вставить эмодзи
	if random.random() < 0.3:
		text += " " + random.choice(emojis)

	# шанс опечатки
	if random.random() < 0.2 and len(text) > 5:
		pos = random.randint(1, len(text) - 2)
		text = text[:pos] + text[pos + 1:] + text[pos] + text[pos + 2:]

	return text