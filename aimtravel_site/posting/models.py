from django.db import models

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

    news_image = models.URLField(
        blank=True,
        null=True,
    )

    def __str__(self):
        result = f'{self.news_title}'
        return result


class MainFeedback(models.Model):
    class Meta:
        verbose_name = 'Feedback Начална страница'
        verbose_name_plural = 'Feedback Начална страница'

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
    feedback_2_title = models.CharField(
        verbose_name='Заглавие',
        max_length=TITLE,
        blank=True,
        null=True,
    )
    feedback_2_content = models.TextField(
        verbose_name='Съдържание',
        blank=True,
        null=True,
    )
    feedback_2_image = models.ImageField(
        upload_to='main_feedback_pics/',
        verbose_name='Снимка',
        blank=True,
        null=True,
    )
    feedback_3_title = models.CharField(
        verbose_name='Заглавие',
        max_length=TITLE,
        blank=True,
        null=True,
    )
    feedback_3_content = models.TextField(
        verbose_name='Съдържание',
        blank=True,
        null=True,
    )
    feedback_3_image = models.ImageField(
        upload_to='main_feedback_pics/',
        verbose_name='Снимка',
        blank=True,
        null=True,
    )


class AdditionalFeedback(models.Model):
    class Meta:
        verbose_name = 'Feedback допълнителна страница'
        verbose_name_plural = 'Feedback допълнителна страница'

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
        upload_to='additional_feedback_pics/',
        verbose_name='Снимка',
        blank=True,
        null=True,
    )
    feedback_2_title = models.CharField(
        verbose_name='Заглавие',
        max_length=TITLE,
        blank=True,
        null=True,
    )
    feedback_2_content = models.TextField(
        verbose_name='Съдържание',
        blank=True,
        null=True,
    )
    feedback_2_image = models.ImageField(
        upload_to='additional_feedback_pics/',
        verbose_name='Снимка',
        blank=True,
        null=True,
    )
    feedback_3_title = models.CharField(
        verbose_name='Заглавие',
        max_length=TITLE,
        blank=True,
        null=True,
    )
    feedback_3_content = models.TextField(
        verbose_name='Съдържание',
        blank=True,
        null=True,
    )
    feedback_3_image = models.ImageField(
        upload_to='additional_feedback_pics/',
        verbose_name='Снимка',
        blank=True,
        null=True,
    )