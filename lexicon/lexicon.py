LEXICON: dict[str, str] = {
# Команды
    'greeting':'<b>«Помощник юриста»</b> — Ваш надежный цифровой партнер в юридических вопросах, '
               'созданный для упрощения работы с юридическими делами, отслеживания судебных процессов '
               'и автоматизации рутинных расчетов. Он идеально подходит как для профессиональных юристов, '
               'так и для граждан, самостоятельно отстаивающих свои права.\n'
               'Введите или нажмите /help, чтобы увидеть возможности бота.\n'
               'Введите или нажмите /support, для связи с поддержкой.\n'
               'Нажмите на кнопку "Главное меню", чтобы начать работу.',

    'help': 'Ключевые возможности:\n'
            '📂 Управление делами\n'
            '— Храните всю информацию о делах в одном месте: название, суд, номер дела, статус.\n'
            '— Легко добавляйте, редактируйте или удаляйте дела через интуитивное меню.\n'
            '— Быстрый доступ к списку дел с возможностью фильтрации и поиска.\n\n'
            '⚖️ Контроль судебных заседаний\n'
            '— Получайте напоминания о ближайших заседаниях (за 2 дня и в день события).\n'
            '— Просматривайте дату, время, адрес суда и связанное дело в одном сообщении.\n'
            '— Ни одно важное слушание не останется без внимания.\n\n'
            '🧮 Юридические калькуляторы\n'
            '— Автоматический расчет госпошлины для исковых заявлений.\n'
            '— Определение сроков исковой давности, пеней, неустоек и компенсаций.\n'
            '— Простые шаблоны для ввода данных и мгновенный результат.',
# Инлайн кнопки
    'menu': '⚖️ Главное меню',

    'main_menu': 'Добро пожаловать, {}!\n\n'
            'Выберите нужную вкладку:\n\n'
            '🗃 <b>Мои дела</b> – просмотр и управление вашими делами.\n\n'
            '⚖️ <b>Судебные заседания</b> – ближайшие слушания и напоминания.\n\n'
            '🧮 <b>Юридические калькуляторы</b> – расчет госпошлины, сроков и других параметров.\n\n'
            '🛎 <b>Настройка уведомлений</b> - управление напоминаниями о заседаниях.',

    'case': '🗃 Мои дела',
    'court_sessions': '⚖️ Судебные заседания',
    'calculators': '🧮 Юридические калькуляторы',
    'setting_notifications': '🛎 Настройка уведомлений',

    'not_empty_cases': '📂 <b>Ваши дела</b>\n\n'
            '<i>Здесь вы можете управлять списком дел:</i>',

        'chosen_user_case': '⚖️ <i>Дело:</i> {case_name}\n'
                            '▫️ <b>Суд:</b> {court_name}\n'
                            '▫️ <b>Номер дела:</b> <code>{case_number}</code>\n'
                            '▫️ <b>Дата и время заседания:</b> {session_date}',
        'case_not_found': 'Дело не найдено.',

        'found_sessions': '⚖️ Ваши судебные заседания:\n\n',
        'empty_sessions': 'Судебные заседания не найдены.',

            'add_s_d': '⏰ Добавить дату судебного заседания',
                'enter_court_session': 'Введите дату судебного заседания в формате ДД.ММ.ГГГГ ЧЧ:ММ',
                'confirm_add_session': 'Дата судебного заседания успешно добавлена ✔️',
            'update_s_d': '⏰ Обновить дату судебного заседания',
                'confirm_update_session': 'Дата судебного заседания успешно обновлена ✔️',

            'edit_case': '✏️ Редактировать дело',
                'choice_edit_case': '✏️ <b>Редактирование дела</b>\n\n'
                                    'Выберете параметры, которые хотите изменить:',
                'ed_case_name': '✏️ Редактировать название дела',
                'ed_case_number': '✏️ Редактировать номер дела',
                'ed_court_name': '✏️ Редактировать название суда',

            'delete_case': '🗑️ Удалить дело',
                'confirm_delete': '❌ Вы уверены, что хотите удалить дело «{}»?',
                'yes_delete': '✔️ Да, удалить',
                'no_cancel': '❌ Нет, отмена',
                'delete_confirmation': 'Дело {case_name} успешно удалено.',

        'add_case': '📥 Добавить новое дело',
            'add_case_name': '<b>Введите название дела:</b>',
            'add_case_number': '<b>Введите номер судебного дела в суде:</b>',
            'add_court_name': '<b>Введите название суда в производстве которого находится дело:</b>',
            'checking_added': 'Вы хотите добавить дело со следующей информацией:\n\n'
                              '⚖️ <i>Дело:</i> {case_name}\n'
                              '▫️ <b>Суд:</b> {court_name}\n'
                              '▫️ <b>Номер дела:</b> {case_number}\n\n'
                              'Все верно?',
                'confirm_added': '✔️ Да, добавить',
                'cancel_added': '❌ Нет, отмена',
            'successfully_add_case': 'Дело <b>{}</b> успешно добавлено ✔️',
        'back_menu': '🔙 Вернуться в меню',
    'empty_cases': '📭 Список дел пуст. Хотите добавить первое дело?',

    'notifications_menu': '🛎 Настройка уведомлений\n\n'
                          'Управляйте напоминаниями о заседаниях: включите или выключите их одним нажатием.\n'
                          'Текущий статус уведомлений: <b>{}</b>',
    'turn_on': '✔️ Включить уведомления',
    'turn_off': '❌ Выключить уведомления',

    'error': 'Ошибка: пользователь не найден или некорректный запрос.',
    'back': 'Назад',
}

LEXICON_COMMANDS: dict[str, str] = {
    '/menu': 'Главное меню',
    '/help': 'Помощь',
    '/support': 'Поддержка'
}