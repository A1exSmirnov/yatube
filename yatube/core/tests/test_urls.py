from http import HTTPStatus
from django.test import TestCase, Client

from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Smirnov')
        cls.group = Group.objects.create(
            title='Тестовая группа title',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа text',
        )

    def setUp(self):
        self.guest_client = Client()

    def test_404_page_uses_correct_template(self):
        """Страница 404 использует кастомный шаблон."""
        response = self.guest_client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
