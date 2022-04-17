import sqlite3


def sql_crate():
    global db, cursor
    db = sqlite3.connect("bot.sqlite3")
    cursor = db.cursor()
    if db:
        print("Database connected!")
    db.execute("CREATE TABLE IF NOT EXISTS anketa "
               "(photo TEXT, name TEXT, surname TEXT, age INTEGER, tag TEXT PRIMARY KEY,"
               "gender TEXT, is_student BOOL, is_teacher BOOL, is_admin BOOL)")
    db.commit()


async def sql_command_insert(state):
    async with state.proxy() as data:
        cursor.execute("INSERT INTO anketa VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", tuple(data.values()))
        db.commit()


async def sql_command_all(message):
    return cursor.execute("SELECT * FROM anketa").fetchall()


async def sql_command_delete(data):
    cursor.execute("DELETE FROM anketa WHERE tag == ?", (data,))
    db.commit()
