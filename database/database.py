import aiosqlite


# Преобразование списка кортежей с делами пользователя в словарь словарей
def transform_massive_cases(cases: list[tuple]) -> dict[int, dict[str, str | int]]:
    dict_cases = {}
    keys = ('case_name', 'court_nuber_case', 'court_name', 'court_session')
    for case in cases:
        dict_cases[case[0]] = dict(zip(keys, case[2:]))
    return dict_cases


# Функция создания БД и таблиц users и states
async def create_db() -> None:
    async with aiosqlite.connect('database/db.db') as db:
        await db.execute('CREATE TABLE IF NOT EXISTS users '
                         '(user_id integer, username text, full_name text, PRIMARY KEY(user_id))')
        await db.execute('CREATE TABLE IF NOT EXISTS cases '
                         '(case_id integer, user_id integer, case_name text, court_case_name text, court text, '
                         'court_session text, PRIMARY KEY(case_id AUTOINCREMENT))')
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
async def add_case_in_db(user_id: int, case: dict[str, str]) -> int:
    async with aiosqlite.connect('database/db.db') as db:
        cursor = await db.execute('INSERT INTO cases (user_id, case_name, court_case_name, court) VALUES (?, ?, ?, ?)',
                                  (user_id, case['case_name'], case['court_case_name'], case['court']))
        case_id = cursor.lastrowid
        await db.commit()
        return case_id


# Получение списка дел пользователя из БД states
async def get_user_cases(user_id: int) -> dict[int, dict[str, str | int]] | None:
    async with aiosqlite.connect('database/db.db') as db:
        cases_user = await db.execute('SELECT * FROM cases WHERE user_id = ?', (user_id,))
        cases_user = await cases_user.fetchall()
        if cases_user:
            # Если есть добавленные дела, то возвращает словарь словарей дел
            # print(cases_user)
            return transform_massive_cases(cases_user)
        else:
            return None


# Получение конкретного дела из списка пользователя
async def fetch_chosen_case(user_id: int, case_name: str) -> str:
    async with aiosqlite.connect('database/db.db') as db:
        user_case = await db.execute('SELECT * FROM cases WHERE (user_id = ? AND case_name = ?)',
                                     (user_id, case_name))
        user_case = await user_case.fetchone()
        user_dict_case = (f'Название дела: {user_case[2]}\n'
                            f'id дела: {user_case[0]}\n'
                            f'Название суда: {user_case[4]}\n'
                            f'Номер дела в суде: {user_case[3]}')
        return user_dict_case


# Удаление дела из списка
async def delete_case_from_list(user_id: int, case_name: str):
    async with aiosqlite.connect('database/db.db') as db:
        await db.execute('DELETE FROM cases WHERE (user_id = ? AND case_name = ?)',
                         (user_id, case_name))
        await db.commit()
