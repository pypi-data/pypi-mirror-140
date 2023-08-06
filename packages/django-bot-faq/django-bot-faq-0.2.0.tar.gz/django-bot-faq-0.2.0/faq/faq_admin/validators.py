from django.core.exceptions import ValidationError

import re


def image_size_validate(value):
	if value.size > 5_000_000:
		raise ValidationError("Превышен допустимый размер в 5 MB!")


def image_types_validate(value):
	file_type = value.name.split('.')[-1]

	if file_type not in ('png', 'jpg', 'jpeg', 'gif', 'webp'):
		raise ValidationError(
			"Недопустимое расширение файла! "
			"Допускаются только 'png', 'jpg', 'jpeg', 'gif', 'webp'"
		)


def tags_in_text_validate(value):
	open_tags = ('<b', '<strong', '<i', '<em', '<u', '<ins', '<s', '<strike', '<del', '<tg-spoiler', '<code', '<pre', '<a href=')
	close_tags = ('</b>', '</strong>', '</i>', '</em>', '</u>', '</ins>', '</s>', '</strike>', '</del>', '</tg-spoiler>', '</code>', '</pre>', '</a>')
	err = ValidationError(
		"В тексте есть незакрытые теги!"
		"Проверьте правильность написания."
		"Примеры находятся по ссылке https://core.telegram.org/bots/api#html-style"
	)

	if '<' in value or '>' in value:
		if len(re.findall(r'[<>]', value)) % 4 != 0:
			raise err

		else:
			for open_tag, close_tag in zip(open_tags, close_tags):
				if open_tag in value and close_tag not in value or close_tag in value and open_tag not in value:
					raise err
