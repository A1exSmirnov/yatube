from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа title проверка __str__',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа text проверка __str__',
        )

    def setUp(self):
        self.post = PostModelTest.post
        group = PostModelTest.group
        post = PostModelTest.post
        title = group.title
        text = post.text[:15]
        self.expected_str = {
            title: group,
            text: post,
        }
        self.field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'group': 'Группа',
            'author': 'Автор',
        }
        self.field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        for field, expected_value in self.expected_str.items():
            with self.subTest(field=field):
                self.assertEqual(
                    field, str(expected_value))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        for field, expected_value in self.field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        for field, expected_value in self.field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value)
