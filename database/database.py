import aiosqlite
from datetime import datetime


# Преобразование списка кортежей с делами пользователя в словарь словарей
def transform_massive_cases(cases: list[tuple]) -> dict[int, dict[str, str | int]]:
    dict_cases = {}
    keys = ('case_name', 'court_nuber_case', 'court_name', 'court_session')
    for case in cases:
        dict_cases[case[0]] = dict(zip(keys, case[2:]))
    return dict_cases


# Функция создания БД и таблиц users, cases, sessions
async def create_db() -> None:
    async with aiosqlite.connect('database/db.db') as db:
        # Таблица users с информацией о пользователях бота
        await db.execute('CREATE TABLE IF NOT EXISTS users '
                         '(user_id integer, username text, full_name text, PRIMARY KEY(user_id))')
        # Таблица cases с информацией о делах пользователей
        await db.execute('CREATE TABLE IF NOT EXISTS cases '
                         '(case_id integer, user_id integer, case_name text, court_case_name text, court text, '
                         'PRIMARY KEY(case_id AUTOINCREMENT))')
        # Таблица sessions с информацией о датах судебных заседаний пользователей
        await db.execute('CREATE TABLE IF NOT EXISTS sessions '
                         '(session_id integer, case_id integer, date text, PRIMARY KEY(session_id AUTOINCREMENT))')
        await db.commit()


# Добавление пользователя в БД таблицу users
async def process_add_user(user_id: int, username: str, full_name: str) -> None:
    async with aiosqlite.connect('database/db.db') as db:
        check_user = await db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        check_user = await check_user.fetchone()
        if check_user is None:
            await db.execute('INSERT INTO users (user_id, username, full_name) VALUES (?, ?, ?)',
                             (user_id, username, full_name))
            await db.commit()


# Добавление дела в БД таблицу cases
async def add_case_in_db(user_id: int, case: dict[str, str]):
    async with aiosqlite.connect('database/db.db') as db:
        cursor = await db.execute('INSERT INTO cases (user_id, case_name, court_case_name, court) '
                                  'VALUES (?, ?, ?, ?)',
                                  (user_id, case['case_name'], case['court_case_name'],
                                   case['court']))
        await db.commit()


# Получение списка дел пользователя из БД states
async def get_user_cases(user_id: int) -> dict[int, dict[str, str | int]] | None:
    async with aiosqlite.connect('database/db.db') as db:
        cases_user = await db.execute('SELECT * FROM cases WHERE user_id = ?', (user_id,))
        cases_user = await cases_user.fetchall()
        if cases_user:
            # Если есть добавленные дела, то возвращает словарь словарей дел
            return transform_massive_cases(cases_user)
        else:
            return None


# Получение выбранного дела из списка пользователя
async def fetch_chosen_case(user_id: int, case_name: str) -> tuple | None:
    # Удаление столбца court_session. Пока не решил удалять или нет.
    # async with aiosqlite.connect('database/db.db') as db:
    #     await db.execute('ALTER TABLE cases DROP COLUMN court_session')
    #     await db.commit()
    try:
        async with aiosqlite.connect('database/db.db') as db:
            user_case = await db.execute('SELECT * FROM cases WHERE (user_id = ? AND case_name = ?)',
                                         (user_id, case_name))
            user_case = await user_case.fetchone()
            return user_case
    except Exception as e:
        print(f'Дело не найдено {e}')
        return None

# Добавление даты заседания в БД
async def add_court_date(case_id: int, date_time: datetime):
    async with aiosqlite.connect('database/db.db') as db:
        await db.execute('INSERT INTO sessions (case_id, date) VALUES (?, ?)',
                   (case_id, date_time.isoformat()))
        await db.commit()


# Редактирование выбранного дела
async def edit_case_from_list(user_id: int, case_name: str, column: str, new_value: str) -> str:
    db_query = f'UPDATE cases SET {column} = ? WHERE (user_id = ? AND case_name = ?)'
    try:
        async with aiosqlite.connect('database/db.db') as db:
            await db.execute(db_query, (new_value, user_id, case_name))
            await db.commit()
            return f'{case_name} успешно отредактирован'
    except Exception as e:
        return f'Произошла ошибка {e}'


# Удаление дела из списка
async def delete_case_from_list(user_id: int, case_name: str) -> str:
    try:
        async with aiosqlite.connect('database/db.db') as db:
            await db.execute('DELETE FROM cases WHERE (user_id = ? AND case_name = ?)',
                             (user_id, case_name))
            await db.commit()
            return 'Дело успешно удалено'
    except Exception as e:
        return f'Произошла ошибка при удалении {e}'
