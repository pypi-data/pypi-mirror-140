from django.contrib.postgres.search import TrigramSimilarity

from typing import Optional, Union

from faq.db_elastic.engine import es
from .models import FAQArticle, FAQArticleContent


def _add_article_transition(article: Optional[FAQArticle] = None):
    if article:
        article.transitions += 1
        article.save()


def get_faq_article(article_id: Union[str, int]):
    return FAQArticle.objects.filter(pk=article_id, status=True).first()


def get_faq_article_n_content(article_id: int):
    article = FAQArticle.objects.prefetch_related('content').get(
        id=article_id,
        status=True
    )
    _add_article_transition(article=article)

    return article, article.content.all()


def get_articles_by_level(article_id: Union[str, int, None] = None):
    if article_id:
        return FAQArticle.objects.filter(article_id=article_id, status=True)

    else:
        return FAQArticle.objects.filter(level=0, status=True)


def trigram_search(text: str, score: float = 0.3):
    articles = list(FAQArticle.objects.annotate(
        similarity=TrigramSimilarity('title', text)
                   + TrigramSimilarity('text', text)
    ).filter(similarity__gt=score).order_by('-similarity'))

    contents = [c.article for c in
                FAQArticleContent.objects.annotate(
                    similarity=TrigramSimilarity('text', text)
                ).filter(similarity__gt=score).order_by('-similarity')]

    return articles + contents  # articles have priority


def search_faq_by_text(text: str, answer_count: int = 5):
    answers = es.search_faq(text)                       # ElasticSearch

    if answers:
        articles = []

        for i, _ in answers[:answer_count]:
            if article := get_faq_article(article_id=i):
                articles.append(article)

    else:
        articles = trigram_search(text)[:answer_count]  # Trigram similarity

    return articles
