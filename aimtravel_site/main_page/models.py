from django.db import models

# Create your models here.


class MainSlider(models.Model):
    class Meta:
        verbose_name = 'Слайдер'
        verbose_name_plural = '1. Основен слайдер'

    title1 = models.CharField(
        verbose_name="Голямо заглавие",
        max_length=255,
        blank=True,
        null=True,
    )
    title2 = models.CharField(
        verbose_name="Малко заглавие",
        max_length=255,
        blank=True,
        null=True,
    )
    button_text = models.CharField(
        verbose_name="Бутон - текст",
        max_length=30,
        blank=True,
        null=True,
    )
    button_link = models.CharField(
        verbose_name="Бутон - линк",
        max_length=255,
        blank=True,
        null=True,
    )


class SecondSlider(models.Model):
    class Meta:
        verbose_name = 'Слайдер'
        verbose_name_plural = '2. Втори слайдер'

    title1 = models.CharField(
        verbose_name='Малко заглавие',
        max_length=255,
        blank=True,
        null=True,
    )
    title2 = models.CharField(
        verbose_name='Голямо заглавие',
        max_length=255,
        blank=True,
        null=True,
    )
    content1 = models.CharField(
        verbose_name='Съдържание - първи ред',
        max_length=255,
        blank=True,
        null=True,
    )
    content2 = models.CharField(
        verbose_name='Съдържание - втори ред',
        max_length=255,
        blank=True,
        null=True,
    )
    button_text = models.CharField(
        verbose_name="Бутон - текст",
        max_length=30,
        blank=True,
        null=True,
    )
    button_link = models.CharField(
        verbose_name="Бутон - линк",
        max_length=255,
        blank=True,
        null=True,
    )


class ThirdSlider(models.Model):
    class Meta:
        verbose_name = 'Слайдер'
        verbose_name_plural = '3. Трети слайдер'

    top_title = models.CharField(
        verbose_name='Малко заглавие',
        max_length=255,
        blank=True,
        null=True,
    )
    main_title = models.CharField(
        verbose_name="Голямо заглавие",
        max_length=255,
        blank=True,
        null=True,
    )
    content1 = models.TextField(
        verbose_name='Съдържание',
        blank=True,
        null=True,
    )
    button_text = models.CharField(
        verbose_name="Бутон - текст",
        max_length=30,
        blank=True,
        null=True,
    )
    button_link = models.CharField(
        verbose_name="Бутон - линк",
        max_length=255,
        blank=True,
        null=True,
    )


class ForthSlider(models.Model):
    class Meta:
        verbose_name = 'Слайдер'
        verbose_name_plural = '4. Четвърти слайдер'

    top_title = models.CharField(
        verbose_name='Малко заглавие',
        max_length=255,
        blank=True,
        null=True,
    )
    main_title = models.CharField(
        verbose_name='Голямо заглавие',
        max_length=255,
        blank=True,
        null=True,
    )
    content1 = models.TextField(
        verbose_name='Съдържание',
        blank=True,
        null=True,
    )
    button_text = models.CharField(
        verbose_name="Бутон - текст",
        max_length=30,
        blank=True,
        null=True,
    )
    button_link = models.CharField(
        verbose_name="Бутон - линк",
        max_length=255,
        blank=True,
        null=True,
    )


class AboutSection(models.Model):
    class Meta:
        verbose_name = '"За нас"'
        verbose_name_plural = '5. Секция "За нас"'

    title = models.CharField(
        verbose_name='Заглавие',
        max_length=255,
        blank=True,
        null=True,
    )
    content1 = models.TextField(
        verbose_name='Съдържание 1',
        blank=True,
        null=True,
    )
    content2 = models.TextField(
        verbose_name='Съдържание 2',
        blank=True,
        null=True,
    )
    button_text = models.CharField(
        verbose_name="Бутон - текст",
        max_length=30,
        blank=True,
        null=True,
    )
    button_link = models.CharField(
        verbose_name="Бутон - линк",
        max_length=255,
        blank=True,
        null=True,
    )


class CallToActionSection(models.Model):
    class Meta:
        verbose_name = 'Call to Action'
        verbose_name_plural = '6. Секция "Call to Action"'

    title1 = models.CharField(
        verbose_name='Малко заглавие отгоре',
        max_length=255,
        blank=True,
        null=True,
    )
    title2 = models.CharField(
        verbose_name='Голямо заглавие основно',
        max_length=255,
        blank=True,
        null=True,
    )
    title3 = models.CharField(
        verbose_name='Малко заглавие отдолу',
        max_length=255,
        blank=True,
        null=True,
    )
    content1 = models.TextField(
        verbose_name='Съдържание',
        blank=True,
        null=True,
    )
    button_text = models.CharField(
        verbose_name="Бутон - текст",
        max_length=30,
        blank=True,
        null=True,
    )
    button_link = models.CharField(
        verbose_name="Бутон - линк",
        max_length=255,
        blank=True,
        null=True,
    )


class Video(models.Model):
    class Meta:
        verbose_name = 'Видео'
        verbose_name_plural = '7. Секция "Видеа"'

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
    button_text = models.CharField(
        verbose_name="Бутон - текст",
        max_length=30,
        blank=True,
        null=True,
    )
    button_link = models.CharField(
        verbose_name="Бутон - линк",
        max_length=255,
        blank=True,
        null=True,
    )


class MainPricingSection(models.Model):
    class Meta:
        verbose_name = 'Цени'
        verbose_name_plural = '8. Секция "Цени"'

    title1 = models.CharField(
        verbose_name='Малко заглавие отгоре',
        max_length=255,
        blank=True,
        null=True,
    )
    title2 = models.CharField(
        verbose_name='Голямо заглавие основно',
        max_length=255,
        blank=True,
        null=True,
    )
    title3 = models.CharField(
        verbose_name='Малко заглавие отдолу',
        max_length=255,
        blank=True,
        null=True,
    )
    content1 = models.TextField(
        verbose_name="Съдържание",
        blank=True,
        null=True,
    )
    button_text = models.CharField(
        verbose_name="Бутон - текст",
        max_length=30,
        blank=True,
        null=True,
    )
    button_link = models.CharField(
        verbose_name="Бутон - линк",
        max_length=255,
        blank=True,
        null=True,
    )


class MainServicesSection(models.Model):
    class Meta:
        verbose_name = 'Услуги'
        verbose_name_plural = '9. Секция "Услуги"'

    title1 = models.CharField(
        verbose_name="Заглавие 1",
        max_length=255,
        blank=True,
        null=True,
    )
    content1 = models.TextField(
        verbose_name='Съдържание 1',
        blank=True,
        null=True,
    )
    title2 = models.CharField(
        verbose_name="Заглавие 2",
        max_length=255,
        blank=True,
        null=True,
    )
    content2 = models.TextField(
        verbose_name="Съдържание 2",
        blank=True,
        null=True,
    )
    title3 = models.CharField(
        verbose_name="Заглавие 3",
        max_length=255,
        blank=True,
        null=True,
    )
    content3 = models.TextField(
        verbose_name="Съдържание 3",
        blank=True,
        null=True,
    )
    title4 = models.CharField(
        verbose_name="Заглавие 4",
        max_length=255,
        blank=True,
        null=True,
    )
    content4 = models.TextField(
        verbose_name="Съдържание 4",
        blank=True,
        null=True,
    )
    title5 = models.CharField(
        verbose_name="Заглавие 5",
        max_length=255,
        blank=True,
        null=True,
    )
    content5 = models.TextField(
        verbose_name="Съдържание 5",
        blank=True,
        null=True,
    )
    title6 = models.CharField(
        verbose_name="Заглавие 6",
        max_length=255,
        blank=True,
        null=True,
    )
    content6 = models.TextField(
        verbose_name="Съдържание 6",
        blank=True,
        null=True,
    )