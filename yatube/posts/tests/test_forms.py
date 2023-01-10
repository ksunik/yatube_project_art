import shutil
import tempfile
from posts.models import Group, Post, User
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        
        cls.group1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test_slug_group_1',
            description='Тестовое описание 1',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_group_2',
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста 1',
            group=cls.group1
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами 
        # для управления файлами и директориями: 
        # создание, удаление, копирование, перемещение, изменение папок и файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

        
    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        # Подготавливаем данные для передачи в форму
        small_gif = (            
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст поста 2',
            'group': PostFormTest.group1.id,
            'image': uploaded,
        }
        response = PostFormTest.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('posts:profile', kwargs={'username': PostFormTest.user}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count+1)
        # Проверяем, что создалась запись с нашим слагом
        self.assertTrue(
            Post.objects.filter(
                text = 'Тестовый текст поста 2',
                image='posts/small.gif',
                # group='Тестовая группа 1',
                ).exists()
        )



    def test_post_edit(self):
            """ Изменение текста и группы при отправке валидной формы. """
            form_data = {
                'text': 'Текст изменён',
                'group': PostFormTest.group2.id
            }
            response = PostFormTest.authorized_client.post(
                reverse('posts:post_edit', kwargs={'post_id': PostFormTest.post.pk}),
                data=form_data,
                follow=True
            )
            self.assertEqual(response.status_code, 200)
            # Проверяем, что текст изменился
            self.assertEqual(Post.objects.get(pk=PostFormTest.post.pk).text, form_data['text'])
            # Проверяем, что группа изменился
            self.assertEqual(Post.objects.get(pk=PostFormTest.post.pk).group.id, form_data['group'])

