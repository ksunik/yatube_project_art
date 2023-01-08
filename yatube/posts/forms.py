from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст',
            'group': 'Группа',
            'image': 'Картинка'
        }
        help_texts = {
            'text': 'Введите текст посттав',
            'group': 'Выберите значение из выпадающего списка',
            'image': 'Загрузите нужную картинку'
        }
