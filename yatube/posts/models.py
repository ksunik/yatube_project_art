from django.db import models
from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()

class Group(models.Model):
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    slug = models.SlugField(verbose_name="Слаг")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Автор"
    )
    group = models.ForeignKey(Group(), null=True, blank=True, on_delete=models.CASCADE, related_name='group', verbose_name="Группа") 

    class Meta:
        ordering = ['-pub_date']
        default_related_name = 'posts'

        def __str__(self):
            return self.text[:30]
