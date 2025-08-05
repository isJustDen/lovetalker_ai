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
	dislikes  INTEGER DEFAULT 0
	)
	""")
	conn.commit()
	conn.close()

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

# получение профиля
def get_user(user_id: int):
	conn = get_connection()
	cur = conn.cursor()

	cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
	user = cur.fetchone()

	conn.close()
	return user

# поставить лайк
def add_like(user_id:int):
	conn = get_connection()
	cur = conn.cursor()

	cur.execute("UPDATE users SET likes = likes + 1 WHERE id = ?", (user_id, ))
	conn.commit()
	conn.close()

# поставить дизлайк
def add_dislike(user_id:int):
	conn = get_connection()
	cur = conn.cursor()

	cur.execute("UPDATE users SET dislikes = dislikes + 1 WHERE id = ?", (user_id, ))
	conn.commit()
	conn.close()


