from django.db.models import FileField, ImageField

from typing import Optional, Union
from telebot import TeleBot
from telebot import types as tp

from .keyboards import FAQKeyboards
from .translations import messages as ms
from faq.faq_admin import orm_utils as orm
from bot_storage.storage import BaseStorage


class FAQDispatcher(FAQKeyboards):

    def __init__(self, tbot: TeleBot, storage: BaseStorage,
                 faq_state: str = 'faq_search#', answer_count: int = 5):
        """
        :param tbot: Telegram bot instance
        :param storage: Storage instance for user state & user data
        :param faq_state: State for user FAQ search
        :param answer_count: Search response limit
        """
        self.tb = tbot
        self.st = storage
        self.faq_state = faq_state
        self.answer_count = answer_count
        super().__init__()

    def _send_message(self, chat_id: Union[str, int],
                      mess_text: Optional[str] = None,
                      file: Optional[Union[FileField, ImageField]] = None,
                      markup: Union[tp.ReplyKeyboardMarkup,
                                    tp.ReplyKeyboardRemove,
                                    tp.InlineKeyboardMarkup,
                                    None] = None):
        """
         Base func for sending text messages with or without media-files
        """
        if file:
            if file.name.endswith('.mp4'):
                self.tb.send_video(chat_id, video=file, caption=mess_text,
                                   reply_markup=markup)

            elif file.name.endswith('.gif'):
                self.tb.send_animation(chat_id, animation=file, caption=mess_text,
                                       reply_markup=markup)

            elif file.name.endswith('.webp'):
                self.tb.send_sticker(chat_id=chat_id, sticker=file)
                self.tb.send_message(chat_id, mess_text, reply_markup=markup)

            else:
                self.tb.send_photo(chat_id, photo=file, caption=mess_text,
                                   reply_markup=markup)

        else:
            self.tb.send_message(chat_id, mess_text, reply_markup=markup)

    @staticmethod
    def _caption(obj):
        return f'<b>{obj.title}</b>\n\n{obj.text}'

    def send_faq(self, user_id: Union[str, int],
                 article_id: Union[str, int, None] = None):
        """
         Sends message with your articles

        :param user_id: User's Telegram id
        :param article_id: Article id (from Django DB)
        """

        # set state
        self.st.set_user_state(user_id, state=self.faq_state)

        # send articles
        if article_id:
            if article := orm.get_faq_article(article_id=article_id):
                return self._send_message(
                    chat_id=user_id,
                    mess_text=self._caption(article),
                    file=article.image,
                    markup=self.article_keyboard(
                        articles=orm.get_articles_by_level(article_id=article_id),
                        selected=article_id,
                        back=article.article.id if article.article else ''
                    )
                )

        else:
            if articles := orm.get_articles_by_level():
                return self._send_message(
                    chat_id=user_id,
                    mess_text=ms['MainFAQ']['text_ru'],
                    markup=self.article_keyboard(
                        articles=articles,
                        selected=article_id
                    )
                )

        return self._send_message(
            chat_id=user_id,
            mess_text=ms['NoArticles']['text_ru']
        )

    def send_article(self, user_id: Union[str, int],
                     article_id: Union[str, int]):
        """
         Sends message with concrete article

        :param user_id: User's Telegram id
        :param article_id: Article id (from Django DB)
        """
        article, content = orm.get_faq_article_n_content(article_id=article_id)

        if self.st.get_user_data(user_id).get('state') == self.faq_state:
            back_keyboard = self.back_btn('faq_search#', True)
        else:
            back_keyboard = self.back_btn(f'tree_article#{article_id}', True)

        self._send_message(
            user_id, mess_text=self._caption(obj=article), file=article.image,
            markup=None if content else back_keyboard
        )

        last_cnt_num = content.count() - 1

        for idx, obj in enumerate(content):  # TODO: сделать отправку через CELERY
            self._send_message(
                user_id, mess_text=obj.text, file=obj.image,
                markup=back_keyboard if idx == last_cnt_num else None
            )

    def send_faq_search(self, user_id: Union[str, int],
                        text: Optional[str] = None):
        """
         Sends a search response to a user's text query

        :param user_id: User's Telegram id
        :param text: User's input
        """
        if not text:
            text = self.st.get_user_data(user_id).get('input')

        if answers := orm.search_faq_by_text(text, self.answer_count):
            # set data
            self.st.set_user_data(
                user_id, data={'state': self.faq_state, 'input': text}
            )

            # send articles
            for obj in answers:  # TODO: сделать отправку через CELERY
                self._send_message(
                    user_id, mess_text=self._caption(obj=obj), file=obj.image,
                    markup=self.article_btn(article_id=obj.id, keyboard=True)
                )

        else:
            self._send_message(
                chat_id=user_id,
                mess_text=ms['NothingFound']['text_ru']
            )
