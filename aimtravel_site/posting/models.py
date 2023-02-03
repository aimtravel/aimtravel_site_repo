from django.db import models

# Create your models here.


class News(models.Model):
    POST_NAME = 30
    POST_TITLE = 50

    news_title = models.CharField(
        verbose_name='Заглавие',
        max_length=POST_TITLE,
        blank=True,
        null=True,
    )
    news_content = models.TextField(
        verbose_name='Текст',
        blank=True,
        null=True,
    )
    date = models.DateField(
        verbose_name='дата',
        blank=True,
        null=True,
    )

    news_image = models.URLField(
        blank=True,
        null=True,
    )

    def __str__(self):
        result = f'{self.news_title}'
        return result
