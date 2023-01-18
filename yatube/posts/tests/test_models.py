from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import NUMB_SIBM, Group, Post, User

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост' * 10,
        )


    def test_models_have_correct_object_names_group(self):
        """Проверяем, что у модели group корректно работает __str__."""
        group = PostModelTest.group
        self.assertEqual(str(group), group.title)

    def test_post_str(self):
        post_obj = PostModelTest.post
        expected_obj_name = post_obj.text[:NUMB_SIBM]
        self.assertEqual(str(post_obj), expected_obj_name)

    def test_models_have_correct_object_names_post(self):
        """Проверяем, что у модели post корректно работает __str__."""
        post = PostModelTest.post
        self.assertEqual(str(post), post.text[:NUMB_SIBM]) 

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)  

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)
