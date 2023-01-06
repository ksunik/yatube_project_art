from posts.models import Group, Post, User
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()

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
        

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        # Подготавливаем данные для передачи в форму
        form_data = {
            'text': 'Тестовый текст поста 2',
            'group': PostFormTest.group1.id
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

