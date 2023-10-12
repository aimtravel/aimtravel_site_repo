from django.db import models
from ckeditor.fields import RichTextField

# Create your models here.


class News(models.Model):
    class Meta:
        verbose_name = 'Новини'
        verbose_name_plural = 'Новини'

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
    news_url = models.URLField(
        verbose_name='Линк към Facebook/Instagram',
        blank=True,
        null=True,
    )

    news_image = models.ImageField(
        upload_to='news_pics/',
        verbose_name='Снимка',
        blank=True,
        null=True,
    )

    def __str__(self):
        result = f'{self.news_title}'
        return result


class MainFeedback(models.Model):
    class Meta:
        verbose_name = 'Истории на студенти'
        verbose_name_plural = 'Истории на студенти'

    TITLE = 50

    feedback_1_title = models.CharField(
        verbose_name='Заглавие',
        max_length=TITLE,
        blank=True,
        null=True,
    )
    feedback_1_content = models.TextField(
        verbose_name='Съдържание',
        blank=True,
        null=True,
    )
    feedback_1_image = models.ImageField(
            upload_to='main_feedback_pics/',
            verbose_name='Снимка',
            blank=True,
            null=True,
        )


class Video(models.Model):
    class Meta:
        verbose_name = 'Видео'
        verbose_name_plural = 'Видеа - Начална страница'

    main_video = models.URLField(
        verbose_name='Основно видео',
        blank=True,
        null=True,
    )
    main_video_image = models.ImageField(
            upload_to='video_pics/',
            verbose_name='Корица',
            blank=True,
            null=True,
        )
    video_1 = models.URLField(
        verbose_name='Видео 1',
        blank=True,
        null=True,
    )
    video_1_image = models.ImageField(
        upload_to='video_pics/',
        verbose_name='Корица 1',
        blank=True,
        null=True,
    )
    video_2 = models.URLField(
        verbose_name='Видео 2',
        blank=True,
        null=True,
    )
    video_2_image = models.ImageField(
        upload_to='video_pics/',
        verbose_name='Корица 2',
        blank=True,
        null=True,
    )
    video_3 = models.URLField(
        verbose_name='Видео 3',
        blank=True,
        null=True,
    )
    video_3_image = models.ImageField(
        upload_to='video_pics/',
        verbose_name='Корица 3',
        blank=True,
        null=True,
    )
    video_4 = models.URLField(
        verbose_name='Видео 4',
        blank=True,
        null=True,
    )
    video_4_image = models.ImageField(
        upload_to='video_pics/',
        verbose_name='Корица 4',
        blank=True,
        null=True,
    )
    video_5 = models.URLField(
        verbose_name='Видео 5',
        blank=True,
        null=True,
    )
    video_5_image = models.ImageField(
        upload_to='video_pics/',
        verbose_name='Корица 5',
        blank=True,
        null=True,
    )


class Faq(models.Model):
    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQ'

    faq_title = models.CharField(
        max_length=100,
        verbose_name='Въпрос',
        blank=True,
        null=True,
    )
    faq_description = models.CharField(
        max_length=255,
        verbose_name='Отговор',
        blank=True,
        null=True,
    )
