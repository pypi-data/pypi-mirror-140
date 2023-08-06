# django-bot-faq  
#### _FAQ module_  

## Installation:
```sh
pip install django-bot-faq
```

## Setting up
`YourProject/tbot/storage.py`
```python
from os import getenv

from bot_storage.storage import RedisStorage

storage = RedisStorage(
    host=getenv('REDIS_HOST', 'localhost'),
    username=getenv('REDIS_USER', None),
    password=getenv('REDIS_PASSWORD', None)
)
```
`YourProject/settings.py`
```python
# import your storage
from tbot.storage import storage

# Define your storage for user states & data
BOT_STORAGE = storage


# Add this application definition to INSTALLED_APPS
INSTALLED_APPS = [
    'mptt',
    'django_cleanup',
    'faq.faq_admin',
    'django.contrib.postgres',
    ...
]


# Specify the ELASTICSEARCH host if you want use ElasticSearch, otherwise 
# the search will be done by default using PostgreSQL TrigramSimilarity
ELASTICSEARCH = getenv('ELASTIC_DB', 'http://localhost:9200')
```

## Install and run Redis
More information about installing and running Redis on your system on [this page](https://redis.io/topics/quickstart).

## Install and run ElasticSearch
More information about installing and running ElasticSearch on your system on [this page](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html).

## Create and apply migrations
```sh
python manage.py makemigrations faq_admin tbot_base
python manage.py migrate
```

## Usage
### Handlers
`YourProject/tbot/handlers.py`

```python
from telebot import types
from telebot.apihelper import ApiTelegramException

from tbot_base.bot import tbot  # install faq_tbot-base lib or make your own faq_tbot instance
from faq.faq_tbot.dispatcher import FAQDispatcher

from .storage import storage as st  # your storage for users data

dp = FAQDispatcher(tbot=tbot, storage=st)


@tbot.message_handler(func=lambda msg: msg.text in (dp.FAQ_BTN.text, '/start'))
def send_faq(msg: types.Message):
    dp.send_faq(user_id=msg.from_user.id)


@tbot.message_handler(
    func=lambda msg: st.get_user_state(msg.from_user.id) == 'faq_search#'
)
def send_faq_search(msg: types.Message):
    dp.send_faq_search(user_id=msg.from_user.id, text=msg.text)


@tbot.callback_query_handler(func=lambda call: True)
def callback_inline(call: types.CallbackQuery):
    key, article_id = call.data.split('#')

    if key == 'tree_article':
        dp.send_faq(user_id=call.from_user.id, article_id=article_id)

    elif key == 'show_article':
        dp.send_article(user_id=call.from_user.id, article_id=article_id)

    elif key == 'faq_search':
        dp.send_faq_search(user_id=call.from_user.id)

    # remove the "clock" on the inline button
    try:
        tbot.answer_callback_query(callback_query_id=call.id, text='')
    except ApiTelegramException:
        pass
```
