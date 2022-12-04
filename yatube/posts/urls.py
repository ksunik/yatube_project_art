# posts/urls.py
from django.urls import path

from . import views

# в app_name хранится имя namespace
app_name = 'posts'

urlpatterns = [
    # Главная страница. Будет вызвана функция index() из файла views.py
    path('', views.index, name='var_main_page'),

    # 'var_group_list.html' - это имя переменной в шаблоне DTL, 
    # 'group_list.html/' - значение переменной
    # Теперь все ссылки в DTL можно поменять тут одним махом
    # path('group_list.html/', views.group_list, name='var_group_list.html'),
    path('group/<slug>/', views.group_posts, name='group_slug')
] 