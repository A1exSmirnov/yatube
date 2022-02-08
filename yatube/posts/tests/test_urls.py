from django.test import TestCase, Client

from ..models import Group, Post, User


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
        self.post_id = PostURLTests.post.id
        self.guest_client = Client()
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(PostURLTests.user)
        self.urls = [
            '/',
            '/group/test-slug/',
            '/profile/StasBasov/',
            f'/posts/{self.post_id}/'
        ]
        self.templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/StasBasov/': 'posts/profile.html',
            f'/posts/{self.post_id}/': 'posts/post_detail.html',
            f'/posts/{self.post_id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }

    def test_post_url_exists_at_desired_location(self):
        """
        Страницы:
        '/'
        '/group/<slug:slug>/'
        '/profile/<str:username>/'
        '/posts/<int:post_id>/'
        доступны любому пользователю.
        """
        for url in self.urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_post_edit_url_exists_at_desired_location_author_post(self):
        """Страница /posts/<int:post_id>/edit/ доступна автору поста."""
        response = self.authorized_author.get(f'/posts/{self.post_id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_post_create_url_exists_at_desired_location_authorized(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_redirect_not_author_post_on_home_page(self):
        """
        Страница /posts/<int:post_id>/edit/
        перенаправит авторизованного пользователя,
        но не автора поста,
        на главную страницу.
        """
        response = self.authorized_client.get(
            f'/posts/{self.post_id}/edit/', follow=True
        )
        self.assertRedirects(response, '/')

    def test_post_create_url_redirect_anonymous_on_admin_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    def test_add_comment_url_redirect_anonymous_on_admin_login(self):
        """
        При комментировании поста
        анонимный пользователь
        будет перенаправлен на страницу логина.
        """
        response = self.guest_client.get(f'/posts/{self.post_id}/comment/')
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post_id}/comment/'
        )

    def test_add_comment_url_redirect_authorized_on_post_detail(self):
        """
        При комментировании поста
        зарегистрированный пользователь
        будет перенаправлен на страницу post_detail.
        """
        response = self.authorized_client.get(
            f'/posts/{self.post_id}/comment/'
        )
        self.assertRedirects(
            response, f'/posts/{self.post_id}/'
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in self.templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_author.get(url)
                self.assertTemplateUsed(response, template)


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_author(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_tech(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)
