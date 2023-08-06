messages = {
    'MainMenu': {
        'text_ru': 'Главное меню',
        'buttons': [
            {'reply': True, 'row': 0, 'text_ru': 'FAQ'},
        ]
    },
    'MainFAQ': {
        'text_ru': 'Это FAQ по роботе с клиентмами.\n\n'
                   'Можешь искать с помощью кнопок или по ключевому слову. '
                   'Например "грубость"',
        'buttons': [
            {'callback_data': 'show_article#', 'row': 0, 'text_ru': 'Смотреть статью целиком'},
        ]
    },
    'NoArticles': {
        'text_ru': 'В базе ещё нет ни одной статьи',
    },
    'NothingFound': {
        'text_ru': 'По Вашему запросу ничего не найдено.\nПопробуйте ещё раз',
    },

}
