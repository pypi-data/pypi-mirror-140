from django.db import models
from django.contrib import admin, messages
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe

from .models import FAQArticle, FAQArticleContent
from faq.db_elastic.engine import es


class AdminImageWidget(AdminFileWidget):

    def render(self, name, value, attrs=None, renderer=None):
        output = []

        if value and getattr(value, "url", None):
            image_url = value.url

            output.append(
                f'<a href="{image_url}" target="_blank">'
                f'<img src="{image_url}" alt="{value}" height="200" style="object-fit: cover;"/>'
                f'</a>'

                # Excludes extra fields
                #
                # f'<span class="clearable-file-input">'
                # f'<input type="checkbox" name="image-clear" id="image-clear_id">'
                # f'<label for="image-clear_id">Clear</label>'
                # f'</span><br>Change: '
                # f'<input type="file" name="image" accept="image/*" id="id_image">'
            )

        output.append(super().render(name, value, attrs))

        return mark_safe(u''.join(output))


class FAQArticleContentInline(admin.StackedInline):
    model = FAQArticleContent
    extra = 0
    formfield_overrides = {models.ImageField: {'widget': AdminImageWidget}}


@admin.register(FAQArticle)
class FAQArticleAdmin(admin.ModelAdmin):
    list_display = ('answer_id', 'title', 'get_text',
                    'attribute', 'transitions', 'status')
    list_display_links = ('answer_id', 'title')
    fields = ('get_answer_id', 'title', 'text', 'image',
              'article', 'transitions', 'status')

    list_filter = ('status',)
    search_fields = ('answer_id', 'title', 'text', 'article__title')
    actions = ('status_active', 'status_not_active')

    inlines = [FAQArticleContentInline]

    formfield_overrides = {models.ImageField: {'widget': AdminImageWidget}}

    @admin.display(description='Текст', ordering='text')
    def get_text(self, obj):
        return obj.text[0:50]

    @admin.display(description='Атрибут')
    def attribute(self, obj):
        return mark_safe(
            '<br>'.join(
                x.title for x in FAQArticle.objects.filter(
                    article=obj,
                )
            )
        )

    @admin.display(description='id статьи', ordering='description')
    def get_answer_id(self, obj):
        return 'не указан' if obj.answer_id == '-1' else obj.answer_id

    @admin.display(description='Активный')
    def status_active(self, request, queryset):
        queryset.update(status=True)

    @admin.display(description='Неактивный')
    def status_not_active(self, request, queryset):
        queryset.update(status=False)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return 'transitions', 'get_answer_id', 'article',
        return 'transitions', 'get_answer_id',

    def delete_queryset(self, request, queryset):
        for el in queryset:
            es.delete_elem(obj_id=el.id, index='faq_article')
        queryset.delete()

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for obj in formset.deleted_objects:
            es.delete_elem(obj_id=obj.id, index='faq_article_content')
            obj.delete()

        for instance in instances:
            if instance.text or instance.image:
                instance.save()
                es.update_content(instance=instance)

            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    '"Контент" должен содержать текст и/или картинку'
                )

        formset.save_m2m()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.related_model \
                and request.resolver_match.kwargs.get('object_id'):
            object_id = request.resolver_match.kwargs['object_id']
            kwargs["queryset"] = db_field.related_model.objects.exclude(
                id=object_id
            )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
