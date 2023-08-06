from django.conf import settings

from loguru import logger
from typing import Union, Literal
from elasticsearch import Elasticsearch, exceptions
from elasticsearch_dsl import Q, Search, UpdateByQuery

from .document import FaqArticle, FaqArticleContent


class ElasticEngine(Elasticsearch):
    def __init__(self):
        self.is_active = False

        try:
            super().__init__(hosts=settings.ELASTICSEARCH)

            FaqArticle.init(using=self)
            FaqArticleContent.init(using=self)

            self.is_active = True

        except AttributeError:
            logger.error(
                f"You have not defined the ELASTICSEARCH variable in settings.py"
            )

        except exceptions.ConnectionError as e:
            logger.error(
                f"{e}\n"
                f"____________________________________________________\n"
                f"Maybe you have not started the ElasticSearch service"
                f"\n____________________________________________________"
            )

    def search_faq(self, query: str, status: bool = True):
        """
        :param query: Text for search
        :param status: FAQ status (True = Активный, False = Неактивный)

        :return: [(django_id, score)]
        """

        if self.is_active:
            resp_article = Search(using=self, index='faq_article').query(
                Q('multi_match', query=query, fields=['title', 'text']) &
                Q('match', status=status)
            ).execute()

            resp_content = Search(using=self,
                                  index='faq_article_content').query(
                Q('match', text=query) &
                Q('match', status=status)
            ).execute()

            articles = [(
                sec['_source']['id'],
                sec['_score']
            ) for sec in resp_article['hits']['hits'] if
                sec['_source'].to_dict().get(
                    'id'
                )]

            contents = [(
                sec['_source']['article_id'],
                sec['_score']
            ) for sec in resp_content['hits']['hits'] if
                sec['_source'].to_dict().get(
                    'article_id'
                ) and sec['_source']['article_id'] not in articles[0]]

            return sorted(set(articles + contents), key=lambda hits: hits[1])
        return set()

    def _get_elem(self, obj_id: Union[str, int],
                  index: Literal['faq_article', 'faq_article_content']):
        if self.is_active:
            return Search(using=self, index=index).query("match", id=obj_id).execute()
        return None

    def delete_elem(self, obj_id: Union[str, int],
                    index: Literal['faq_article', 'faq_article_content']):
        if self.is_active:
            Search(using=self, index=index).query("match", id=obj_id).delete()

    def update_article(self, instance):
        if self.is_active:
            elem = self._get_elem(instance.id, index='faq_article')

            if elem:
                UpdateByQuery(
                    using=self,
                    index='faq_article',
                ).query(
                    "match", id=instance.id
                ).script(
                    inline='ctx._source.title = params.local_title; '
                           'ctx._source.text = params.local_text; '
                           'ctx._source.status = params.local_status;',
                    params={
                        "local_title": instance.title,
                        "local_text": instance.text,
                        "local_status": instance.status
                    },
                ).execute()

            else:
                FaqArticle(
                    id=instance.id,
                    title=instance.title,
                    text=instance.text,
                    status=instance.status,
                ).save(using=self)

    def update_content(self, instance):
        if self.is_active:
            elem = self._get_elem(instance.id, index='faq_article_content')

            if elem:
                UpdateByQuery(
                    using=self,
                    index='faq_article_content',
                ).query(
                    "match", id=instance.id
                ).script(
                    inline='ctx._source.text = params.local_text; '
                           'ctx._source.status = params.local_status;',
                    params={
                        "local_text": instance.text,
                        "local_status": instance.article.status
                    },
                ).execute()

            else:
                FaqArticleContent(
                    article_id=instance.article.id,
                    id=instance.id,
                    text=instance.text,
                    status=instance.article.status
                ).save(using=self)


es = ElasticEngine()
