#core/utils.py
import random

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