from django.shortcuts import render, get_object_or_404
from .models import Post, Group


# Create your views here.

# def index(request):
#     # Загружаем шаблон с DTL
#     template = 'posts/index.html'
#     # В словаре можно передавать переменные в DTL
#     context = {'text': 'Это главная страница проекта Yatube'}
#     return render(request, template, context)

def index(request):
    # Одна строка вместо тысячи слов на SQL:
    # в переменную posts будет сохранена выборка из 10 объектов модели Post,
    # отсортированных по полю pub_date по убыванию (от больших значений к меньшим)
    posts = Post.objects.order_by('-pub_date')[:10]
    # В словаре context отправляем информацию в шаблон
    context = {
        'posts': posts,
    }
    return render(request, 'posts/index.html', context)


# def group_list(request):
#     template = 'posts/group_list.html'
#     context = {'text': 'Здесь будет информация о группах проекта Yatube'}
#     return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    context = {
       'group': group,
       'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)




