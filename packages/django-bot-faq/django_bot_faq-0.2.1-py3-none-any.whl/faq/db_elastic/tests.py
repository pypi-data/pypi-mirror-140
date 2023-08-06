from loguru import logger
from elasticsearch_dsl import Search

from .engine import es


def _match_all_article(index='faq_article'):
    return Search(using=es, index=index).query("match_all")


def _match_content(article_id, index='faq_article_content'):
    return Search(using=es, index=index).query("match", article_id=article_id)


def faq_article_delete():
    res = _match_all_article().delete()
    logger.success(res)


def view_faq_articles():
    for art in _match_all_article().execute()['hits']['hits']:
        logger.debug(art['_source'])

        for cont in _match_content(art['_source']['id']).execute()['hits']['hits']:
            logger.info(cont['_source'])
