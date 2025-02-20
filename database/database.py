import aiosqlite

async def create_db():
    async with aiosqlite.connect('database/db.db') as db:
        await db.execute('CREATE TABLE IF NOT EXISTS users '
                         '(user_id integer, username text, full_name text, PRIMARY KEY(user_id AUTOINCREMENT))')
        await db.commit()

# Добавление пользователя в БД
async def process_add_user(user_id: int, username: str, full_name: str) -> None:
    async with aiosqlite.connect('database/db.db') as db:
        check_user = await db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        check_user = await check_user.fetchone()
        if check_user is None:
            await db.execute('INSERT INTO users (user_id, username, full_name) VALUES (?, ?, ?)',
                             (user_id, username, full_name))
            await db.commit()

    # connect = await aiosqlite.connect('database/db.db')
    # cursor = await connect.cursor()
    # check_user = await cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    # check_user = await check_user.fetchone()
    # if check_user is None:
    #     await cursor.execute('INSERT INTO users (user_id, username, full_name) VALUES (?, ?, ?)',
    #                          (user_id, username, full_name))
    #     await connect.commit()
    # await cursor.close()
    # await connect.close()