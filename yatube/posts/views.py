from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Post, Group, User
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from django.shortcuts import redirect



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
    # posts = Post.objects.order_by('-pub_date')[:10]
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # В словаре context отправляем информацию в шаблон
    context = {
        #'posts': posts,
        #'post_list': post_list,
        'page_obj': page_obj,
    }
    template = 'posts/index.html'
    return render(request, 'posts/index.html', context)


# def group_list(request):
#     template = 'posts/group_list.html'
#     context = {'text': 'Здесь будет информация о группах проекта Yatube'}
#     return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    # posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
       'group': group,
       # 'posts': posts,
       'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = User.objects.get(username=username)
    # Здесь код запроса к модели и создание словаря контекста
    posts_user = Post.objects.filter(author=author)
    paginator = Paginator(posts_user, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # В словаре context отправляем информацию в шаблон
    context = {
        #'posts': posts,
        #'post_list': post_list,
        # 'page_obj': page_obj,
        'author': author,
        'posts_user': posts_user,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    author = post.author_id
    count_post = Post.objects.filter(author=author).count()
    
    # Здесь код запроса к модели и создание словаря контекста
    context = {

        # 'author': author,
        #'posts_user': posts_user,
        'count_post': count_post,
        'post': post,

    }
    return render(request, 'posts/post_detail.html', context)    
    

# @login_required
# def post_create(request):
#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#             new_post = form.save(commit=False)
#             new_post.author = request.user
#             new_post.save()
#             return render(request, 'posts/create_post.html', {'form': form})
#             # return redirect('posts:profile', new_post.author)
#     else:
#         form = PostForm()
#         return render(request, 'posts/create_post.html', {'form': form})

@login_required
def post_create(request):
    if request.method == 'POST':
        form_class = PostForm(request.POST)
        if form_class.is_valid():
            new_post = form_class.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('posts:profile', new_post.author)
            # return render(request, 'posts/create_post.html', {'form_class': form_class})
    else:
        form_class = PostForm()
        return render(request, 'posts/create_post.html', {'form_class': form_class})        



@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form_class = PostForm(request.POST or None, instance=post)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    if request.method == 'POST' and form_class.is_valid():
        post.author = request.user
        form_class.save()
        return redirect('posts:post_detail', post_id)
    post = PostForm(instance=post)
    is_edit = True
    context = {
        'form_class': form_class,
        'is_edit': is_edit,
        'post': post,
        'post_id': post_id
    }
    return render(request, 'posts/create_post.html', context)