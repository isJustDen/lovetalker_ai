# core/user_db.py

import sqlite3

# подключение к базе
def get_connection():
	return sqlite3.connect('data/users.db')
#------------------------------------------------------------------------------------------------------------------

# инициализация таблицы users
def init_db():
	conn = get_connection()
	cur = conn.cursor()


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

# таблица диалогов
	cur.execute("""
	CREATE TABLE IF NOT EXISTS dialogs(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id INTEGER,
	sender TEXT,
	message TEXT,
	timestamp INTEGER DEFAULT CURRENT_TIMESTAMP
	)
	""")

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
def save_message(user_id: int, sender: str, message: str):
	conn = get_connection()
	cur = conn.cursor()

	cur.execute("INSERT INTO dialogs (user_id, sender, message) VALUES (?, ?, ?)",
	            (user_id, sender, message)
	            )

	conn.commit()
	conn.close()


#------------------------------------------------------------------------------------------------------------------

# получить историю сообщений с пользователем
def get_dialogs(user_id: int, limit: int = 15):
	conn = get_connection()
	cur = conn.cursor()

	cur.execute("SELECT sender, message, timestamp FROM dialogs WHERE user_id = ? ORDER BY id DESC LIMIT ?",
	            (user_id, limit)
	)

	rows = cur.fetchall()
	conn.close()
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
