import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="django-bot-faq",
	version="0.2.1",
	author="Ivan Romanchenko",
	author_email="vanvanych789@gmail.com",
	description="FAQ module",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/IvanRomanchenko/django-bot-faq",
	packages=[
		"faq",
		"faq.faq_admin",
		"faq.faq_admin.migrations",
		"faq.db_elastic",
		"faq.faq_tbot"
	],
	include_package_data=True,
	classifiers=[
		"Programming Language :: Python :: 3.10",
		"Framework :: Django :: 4.0",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires=">=3.6",
	install_requires=[
		"Django==4.0.2",
		"django-mptt==0.13.4",
		"django-cleanup==6.0.0",
		"Pillow==9.0.1",
		"pyTelegramBotAPI==4.4.0",
		"psycopg2==2.9.3",
		"bot-storage==1.0.1",
		"loguru==0.6.0",
		"elasticsearch==7.17.0",
		"elasticsearch-dsl==7.4.0",
	]
)
