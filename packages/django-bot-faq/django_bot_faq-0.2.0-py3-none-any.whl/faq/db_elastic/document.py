from elasticsearch_dsl import Boolean, Document, Integer, Text


class IndexMixin:
    settings = {
        'number_of_shards': 1,
        'number_of_replicas': 0,
        "analysis": {
            "analyzer": {
                "russian": {
                    "tokenizer": "standard",
                }
            }
        }
    }


class FaqArticle(Document):
    id = Integer()

    answer_id = Text()
    title = Text()
    text = Text()
    status = Boolean()

    class Index(IndexMixin):
        name = 'faq_article'


class FaqArticleContent(Document):
    id = Integer()

    article_id = Integer()
    text = Text()
    status = Boolean()

    class Index(IndexMixin):
        name = 'faq_article_content'
