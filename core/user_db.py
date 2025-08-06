# core/user_db.py
import os
import sqlite3

# подключение к базе
def get_connection():
	db_path = os.path.abspath('data/users.db')
	print(f"Подключаемся к базе по пути: {db_path}")
	conn = sqlite3.connect(db_path)
	conn.execute("PRAGMA journal_mode=WAL")
	conn.execute("PRAGMA synchronous=FULL")
	return conn

#------------------------------------------------------------------------------------------------------------------

# инициализация таблицы users
def init_db():
	conn = get_connection()
	cur = conn.cursor()

	cur.execute("DROP TABLE IF EXISTS paterns")  # Удаляем старую таблицу с опечаткой

	#создание таблицы с информацией о поведении пользователя
	cur.execute("""
	CREATE TABLE IF NOT EXISTS users(
	id INTEGER PRIMARY KEY,
	name TEXT,
	likes INTEGER DEFAULT 0,
	dislikes  INTEGER DEFAULT 0,
	mode TEXT DEFAULT 'assist'
	)
	""")
	# Добавляем столбец mode, если он не существует
	try:
		cur.execute("ALTER TABLE users ADD COLUMN mode TEXT DEFAULT 'assist'")
	except sqlite3.OperationalError:
		pass


#AI‑режим для разных собеседников
	cur.execute("""
	CREATE TABLE IF NOT EXISTS partners(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id INTEGER,
	name TEXT,
	style TEXT DEFAULT "дружелюбный)
	""")


# таблица диалогов
	cur.execute("""
	CREATE TABLE IF NOT EXISTS dialogs(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id INTEGER NOT NULL,
	partner_name TEXT NOT NULL,
	sender TEXT NOT NULL,
	message TEXT NOT NULL,
	timestamp DATATIME DEFAULT CURRENT_TIMESTAMP
	)
	""")
	try:
		cur.execute("ALTER TABLE dialogs ADD COLUMN partner_name TEXT DEFAULT ''")
	except sqlite3.OperationalError:
		pass

	conn.commit()
	conn.close()
#------------------------------------------------------------------------------------------------------------------
# регистрация нового пользователя
def register_user(user_id: int, name: str):
	conn = get_connection()
	cur = conn.cursor()

	cur.execute("SELECT ID FROM users WHERE id = ?", (user_id,))
	result = cur.fetchone()

	if result is None:
		cur.execute("INSERT INTO users (id, name) VALUES (?, ?)", (user_id, name))

	conn.commit()
	conn.close()


#------------------------------------------------------------------------------------------------------------------
# получение профиля
def get_user(user_id: int):
	conn = get_connection()
	cur = conn.cursor()

	cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
	user = cur.fetchone()

	conn.close()
	return user


#------------------------------------------------------------------------------------------------------------------
# поставить лайк
def add_like(user_id:int):
	conn = get_connection()
	cur = conn.cursor()

	cur.execute("UPDATE users SET likes = likes + 1 WHERE id = ?", (user_id, ))
	conn.commit()
	conn.close()


#------------------------------------------------------------------------------------------------------------------
# поставить дизлайк
def add_dislike(user_id:int):
	conn = get_connection()
	cur = conn.cursor()

	cur.execute("UPDATE users SET dislikes = dislikes + 1 WHERE id = ?", (user_id, ))
	conn.commit()
	conn.close()
#------------------------------------------------------------------------------------------------------------------

#сохранение сообщений
def save_message(user_id: int, partner: str, sender: str, message: str):
	conn = get_connection()
	cur = conn.cursor()

	print(f"Сохранение сообщения: user_id={user_id}, partner={partner}, sender={sender}, message={message}")
	cur.execute("INSERT INTO dialogs (user_id, partner_name, sender, message) VALUES (?, ?, ?, ?)",
	            (user_id,partner, sender, message)
	            )

	conn.commit()
	conn.close()


#------------------------------------------------------------------------------------------------------------------

# получить историю сообщений с пользователем
def get_dialogs(user_id: int, partner:str, limit: int = 15):
	conn = get_connection()
	cur = conn.cursor()

	# Проверяем, есть ли диалог с таким партнером
	cur.execute("SELECT 1 FROM dialogs WHERE user_id = ? AND partner_name = ? LIMIT 1",
	            (user_id,partner))
	if not cur.fetchone():
		conn.close()
		return []

	# Получаем историю сообщений
	cur.execute("""SELECT sender, message, timestamp 
						FROM dialogs 
						WHERE user_id = ? AND partner_name = ? 
						ORDER BY timestamp DESC 
						LIMIT ?""",
	            (user_id, partner, limit)
	)
	rows = cur.fetchall()
	conn.close()
	print(f"Получено сообщений для user_id={user_id}, partner={partner}: {len(rows)}")  # Логирование
	return rows[::-1]
#------------------------------------------------------------------------------------------------------------------


#Установка мода общения
def set_mode(user_id:int, mode: str):
	conn = get_connection()
	cur = conn.cursor()
	cur.execute("UPDATE users SET mode = ? WHERE id = ?", (mode, user_id))
	conn.commit()
	conn.close()
#------------------------------------------------------------------------------------------------------------------


# Запрос мода общения
def get_mode(user_id: int):
	conn = get_connection()
	cur = conn.cursor()
	cur.execute("SELECT mode FROM users WHERE id = ?", (user_id, ))
	row = cur.fetchone()
	conn.close()
	return row[0] if row else 'assist'

#Функция для получения списка всех партнеров
def get_partners(user_id: int) -> list:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute("""
	SELECT DISTINCT partner_name FROM dialogs
	WHERE user_id = ?
	""", (user_id,))
	partners = [row[0] for row in cur.fetchall()]
	conn.close()
	return partners

def add_partner(user_id: int, name: str, style: 'дружелюбный'):
	"""Добавление информации о партнере в таблицу"""
	conn = get_connection()
	cur = conn.cursor()

	# Сначала проверяем, существует ли уже такой партнер
	cur.execute("SELECT 1 FROM partners WHERE user_id = ? AND name = ?", (user_id, name))
	if cur.fetchone():
		# Если существует - обновляем стиль
		cur.execute("UPDATE partners SET style = ? WHERE user_id = ? AND name = ?",
		            (style, user_id, name))
	else:
		# Если не существует - добавляем нового
		cur.execute("INSERT INTO partners (user_id, name, style) VALUES (?, ?, ?)",
		            (user_id, name, style))

	conn.commit()
	conn.close()

def get_partner_style(user_id: int, name: str) -> str:
	"""Задаёт стиль, с которым будет происходить общение с партнером"""
	conn = get_connection()
	cur = conn.cursor()

	# Исправлена опечатка в имени столбца (было 'user_id')
	cur.execute("SELECT style FROM partners WHERE user_id = ? AND name = ?",
	            (user_id, name)
	            )
	row = cur.fetchone()
	conn.close()
	return row[0] if row else 'дружелюбный'

def update_partner_style(user_id: int, name: str, style: str):
	conn = get_connection()
	cur = conn.cursor()
	cur.execute("UPDATE partners SET style = ? WHERE user_id = ? and name = ?",
	            (style, user_id, name))
	conn.commit()
	conn.close()