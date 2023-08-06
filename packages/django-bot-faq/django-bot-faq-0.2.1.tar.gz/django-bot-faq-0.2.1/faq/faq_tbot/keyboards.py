from django.db.models.query import QuerySet

from typing import Union
from telebot import types as tp


class DotDict(dict):
    """
     Required for accessing the parameters of the buttons through a dot
        and for the possibility of redefining the values of these parameters
    """

    def __new__(cls, *args, **kwargs):
        self = dict.__new__(cls, *args, **kwargs)
        self.__dict__ = self
        return self


class FAQKeyboards:
    """
     Buttons & markups for FAQ
    """

    def __init__(self):
        self.FAQ_BTN = DotDict(
            text='FAQ',
            callback='faq#'
        )
        self.ARTICLE_BTN = DotDict(
            text='Смотреть статью целиком',
            callback='show_article#'
        )
        self.TREE_BTN = DotDict(
            callback=f'tree_article#'
        )
        self.BACK_BTN = DotDict(
            text='🔙 Назад'
        )

    # ----------------- Reply keyboards -----------------

    def add_faq_reply_btn(self, markup: tp.ReplyKeyboardMarkup) \
            -> tp.ReplyKeyboardMarkup:
        return markup.add(tp.KeyboardButton(text=self.FAQ_BTN.text))

    def faq_reply_keyboard(self, row_width: int = 1) -> tp.ReplyKeyboardMarkup:
        return self.add_faq_reply_btn(markup=tp.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True, row_width=row_width
        ))

    # ----------------- Inline keyboards -----------------

    def back_btn(self, callback: str, keyboard: bool = False) \
            -> Union[tp.InlineKeyboardButton, tp.InlineKeyboardMarkup]:
        btn = tp.InlineKeyboardButton(
            self.BACK_BTN.text, callback_data=callback
        )

        if keyboard:
            return tp.InlineKeyboardMarkup().add(btn)
        return btn

    def article_btn(self, article_id: Union[int, str], keyboard: bool = False) \
            -> Union[tp.InlineKeyboardButton, tp.InlineKeyboardMarkup]:
        btn = tp.InlineKeyboardButton(
            self.ARTICLE_BTN.text,
            callback_data=f'{self.ARTICLE_BTN.callback}{article_id}'
        )

        if keyboard:
            return tp.InlineKeyboardMarkup().add(btn)
        return btn

    def add_faq_inline_btn(self, markup: tp.InlineKeyboardMarkup) \
            -> tp.InlineKeyboardMarkup:
        return markup.add(
            tp.InlineKeyboardButton(text=self.FAQ_BTN.text,
                                    callback_data=self.FAQ_BTN.callback)
        )

    def faq_inline_markup(self, row_width: int = 1) -> tp.InlineKeyboardMarkup:
        return self.add_faq_inline_btn(markup=tp.InlineKeyboardMarkup(
            row_width=row_width
        ))

    def article_keyboard(self, articles: QuerySet,
                         selected: Union[int, str, None] = None,
                         back: Union[int, str, None] = None) \
            -> tp.InlineKeyboardMarkup:
        markup = tp.InlineKeyboardMarkup(row_width=1)

        if selected:
            markup.add(
                self.article_btn(article_id=selected)
            )

        for article in articles:
            markup.add(
                tp.InlineKeyboardButton(
                    article.title,
                    callback_data=f'{self.TREE_BTN.callback}{article.id}'
                )
            )

        if back is not None:
            markup.add(self.back_btn(
                callback=f'{self.TREE_BTN.callback}{back}')
            )

        return markup
