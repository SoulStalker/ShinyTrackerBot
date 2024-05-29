LEXICON_COMMANDS_RU: dict[str, str] = {
    '/start': 'Запуск бота',
    '/help': 'Справка по работе бота',
    '/service': 'Настройка',
    '/contacts': 'Другие способы связи'
}

LEXICON_RU: dict[str, str] = {
    '/start': '<b>Привет!</b>\nЯ помогу тебе следить за временем, '
              'которое ты тратишь на различные задачи\n\nЕсли нужны подробности, '
              'команда /help тебе поможет!\n\nПогнали?',
    '/help': 'Все очень просто. Сначала составляем список направлений, по которым будем работать\n\n'
             'Далее, выбираем направление и запускается время. Пока идет время, ты занимаешься своим делом.\n\n'
             'Как только работа закончена, жмешь кнопку остановки задачи\n\n'
             'Через команду /service можно провести дополнительные настройки бота\n\n'
             'А вечером я выдам тебе статистку\n\nПогнали?',
    '/service': '⚙️ Тут можно задать время для работы задачи до оповещения и время для перерыва\n\n',
    '/contacts': 'По вопросом можно связаться через аккаунт @SoulStalk3r',
    'add_task': '▶️ Добавить задачу',
    '/ads_task': 'Добавляется задача',
    'edit_tasks': '📝 Редактировать задачи',
    '/edit_tasks': '🗑 Нажми на задачу чтобы удалить',
    'choose_category': '🗒 Задача',
    '/choose_category': '❗️Выбери задачу для запуска таймера:',
    'statistics': '📈 Статистика',
    'other_answer': '👀 Это ни на что не похоже',
    'another category': '\n⁉️ Добавить еще задачу?\n\n',
    'task_deleted': '❌ Удалена задача ',
    '/add_task': '✏️ Отправь название задачи или нажми 🚫 <strong>Отмена</strong>',
    'really_add_category': '🆗 Добавить',
    'cancel_add_category': '🚫 Не надо',
    'task_added': '✅ Добавлена задача ',
    'no_user': '⛔ Пользователь не заведен в базе. Нажмите /start для начала',
    'no_category': '😮 Ни одна задача не добавлена. Нажмите добавить задачу для добавления задачи',
    'cancel': '🚫 Отмена',
    '/stop': '🛑 Остановить работу по задаче\n',
    'start_work': '🚀 Начата работа по задаче ',
    'stop_work': '\nДля остановки нажмите на кнопку ниже',
    'task for category': '🔽 Работа по задаче',
    'is stopped': 'остановлена в ',
    'started_at': '\n⏰ Работаем с ',
    'yes': '✅ Да',
    'lets_start': 'Здесь можно создать новую задачу, удалить ненужные задачи,'
                  'начать работу по задаче или посмотреть статистику',
    'success': '🗑 Успешно удалена задача ',
    'incorrect_task_name': '❗️<strong>Задача должна состоять только из букв</strong>\n\n❗️Попробуй еще раз или нажми 👇 <strong>Отмена</strong>',
    'choose_action': 'Выбери действие',
    'task_exist': 'Такая задача уже существует. Введи другое название',
    'total': 'Всего',
    'stats': '🗓 Выбери период для отображения статистики: ',
    'today': 'Сегодня',
    'yesterday': 'Вчера',
    'week': 'Неделя',
    'month': 'Месяц',
    'stats_for': '<strong>Статистика за период</strong> ',
    'del_task': '🗑 Удалить',
    'edit_task': '✏️ Изменить',
    'name_or_color': '❓ Будем менять название задачи или его цвет на графике?',
    'edit_task_name': '🔤 Название',
    'edit_task_color': '🎨 Цвет на графике',
    'edit_task_target': '🎯 Целевое время',
    'del_or_edit_task': 'Удалить задачу или изменить?\n',
    'task_edited': 'Задача изменена',
    'new_task_name': '✏️ Введи новое название для задачи',
    'new_task_color': '✏️ Введи новые цвет для задачи в формате CSS\nНапример "DarkRed" или "#228B22"',
    'new_task_target': '✏️ Введи количество минут, которе хочет тратить на задачу:',
    'chose_task_for_edit': '📝 Нажми на задачу которую хочешь изменить',
    'new_name_of_task': '🆕 Новое название задачи:',
    'new_color_of_task': '🆕 Новый цвет для задачи:',
    'new_target_time': '🆕 Новая цель для задачи:',
    'task_not_exist': '🤷‍♂️ Выбрана несуществующая задача для изменения',
    'edit_work_time': '👨‍💻 Задать длительность задачи',
    'edit_break_time': '🛋 Задать длительность перерыва',
    'new_work_time': 'Новая длительность задачи:',
    'new_break_duration': 'Новая длительность перерыва:',
    'give_new_work_time': 'Введи новое значение для длительности задачи\nили нажми 👇 <strong>Отмена</strong>',
    'give_new_break_time': 'Введи новое значение для длительности перерыва\nили нажми 👇 <strong>Отмена</strong>',
    'current_work_duration': 'Текущая длительность задачи:',
    'current_break_duration': 'Текущая длительность перерыва:',
    'minutes': 'минут',
    'incorrect_duration': '❗️Длительность минут можно задать только в цифрах\n\n❗️Попробуй еще раз или нажми 👇 <strong>Отмена</strong>',
    'time_to_close': '⁉️ <strong>Может пора отдохнуть?</strong>\n\n⏳ Сейчас идет работа по задаче',
    'time_to_work': '<strong>💪 Давай поработаем?</strong>\n\nОтдыхаем уже более',
    'target_time_not_set': 'Не задана',
    'target': 'Цель',
}
