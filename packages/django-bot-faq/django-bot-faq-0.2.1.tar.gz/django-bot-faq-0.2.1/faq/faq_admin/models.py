from django.db import models

from mptt.models import MPTTModel, TreeForeignKey

from faq.db_elastic.engine import es
from .validators import (
    tags_in_text_validate,
    image_size_validate,
    image_types_validate,
)

STATUSES = (
    (True, 'Активный'),
    (False, 'Неактивный'),
)


def _upload_to(instance: models.base.ModelBase, filename: str):
    return f'FAQ/{instance._meta.object_name}/images/{filename}'


class FAQArticle(MPTTModel):
    answer_id = models.CharField(verbose_name='ID статьи',
                                 default='-1', max_length=100,
                                 help_text='заполняется автоматически')
    title = models.CharField(verbose_name='Название', max_length=100,
                             validators=[tags_in_text_validate])
    text = models.TextField(verbose_name='Описание', max_length=900,
                            validators=[tags_in_text_validate])
    image = models.ImageField(verbose_name='Картинка описания',
                              upload_to=_upload_to,
                              blank=True, null=True,
                              validators=[image_size_validate,
                                          image_types_validate])
    article = TreeForeignKey('self', verbose_name='Статья',
                             on_delete=models.CASCADE,
                             null=True, blank=True,
                             related_name='attribute')
    transitions = models.IntegerField(verbose_name='Количество переходов',
                                      default=0)
    status = models.BooleanField(verbose_name='Статус',
                                 choices=STATUSES, default=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_article_id = self.article.id if self.article else None

    def save(self, *args, **kwargs):
        if self.answer_id == '-1' or (
                self.article and self.article.id != self.old_article_id
                    ):
            if self.article:
                pk_answer = FAQArticle.objects.filter(
                    level=self.article.lft,
                    article=self.article
                ).count()

                if not FAQArticle.objects.filter(
                        level=self.article.lft, article=self.article,
                        article__answer_id=f'{self.article.answer_id}.{pk_answer}'
                ) or pk_answer == 0:
                    self.answer_id = f'{self.article.answer_id}.{pk_answer + 1}'

                else:
                    self.answer_id = f'{self.article.answer_id}.{pk_answer}'

            else:
                count = FAQArticle.objects.filter(level=0).count()

                if FAQArticle.objects.filter(
                        answer_id=str(count)
                ) or count == 0:
                    self.answer_id = str(count + 1)

                else:
                    self.answer_id = str(count)

        super().save()

        es.update_article(instance=self)

    def delete(self, *args, **kwargs):
        es.delete_elem(obj_id=self.id, index='faq_article')
        super().delete()

    def __str__(self):
        return f"{self.answer_id}. {self.title}"

    class MPTTMeta:
        order_insertion_by = ['title']
        parent_attr = 'article'

    class Meta:
        ordering = ['answer_id']
        verbose_name = 'FAQ статья'
        verbose_name_plural = 'FAQ статьи'


class FAQArticleContent(models.Model):
    article = models.ForeignKey(FAQArticle, on_delete=models.CASCADE,
                                related_name='content')
    text = models.TextField(verbose_name='Текст', max_length=1000,
                            null=True, blank=True,
                            validators=[tags_in_text_validate])
    image = models.ImageField(verbose_name='Картинка',
                              upload_to=_upload_to,
                              blank=True, null=True,
                              validators=[image_size_validate,
                                          image_types_validate])

    def __str__(self):
        return f"{self.id} -- {self.article}"

    class Meta:
        verbose_name = 'Контент'
        verbose_name_plural = 'Контент'
