import shutil
import tempfile


from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.conf import settings
from django.urls import reverse
from django import forms


from ..models import Group, Post, User, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        cls.user_1 = User.objects.create_user(username='Smirnov')
        cls.user_2 = User.objects.create_user(username='StasBasov')
        cls.user_3 = User.objects.create_user(username='Noname')
        cls.group = Group.objects.create(
            title='Тестовая группа title',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.group_2 = Group.objects.create(
            title='Тестовая группа_2 title',
            slug='any-slug',
            description='Тестовое описание_2',
        )
        cls.post = Post.objects.create(
            author=cls.user_1,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.post_id = PostPagesTests.post.id
        self.post = PostPagesTests.post
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_2)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_3)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.user_1)
        self.templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': self.user_1}):
            ('posts/profile.html'),
            reverse('posts:post_detail', kwargs={'post_id': self.post_id}): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post_id}): (
                'posts/create_post.html'
            ),
        }
        for reverse_name, self.template in self.templates_page_names.items():
            with self.subTest(template=self.template):
                cache.clear()
                self.response_8 = self.authorized_author.get(reverse_name)

        self.form_fields_1 = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        self.form_fields_2 = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        cache.clear()
        response_1 = self.authorized_client.get(reverse('posts:index'))
        first_object_1 = response_1.context['page_obj'][0]
        self.post_author_0 = first_object_1.author
        self.post_text_0 = first_object_1.text
        self.post_group_0 = first_object_1.group

        response_2 = (
            self.authorized_client.
            get(reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        )
        first_object_2 = response_2.context['page_obj'][0]
        self.post_author_1 = first_object_2.author
        self.post_text_1 = first_object_2.text
        self.post_group_1 = first_object_2.group
        response_3 = (
            self.authorized_client.
            get(reverse('posts:profile',
                        kwargs={'username': self.user_1}))
        )
        first_object_3 = response_3.context['page_obj'][0]
        self.post_author_2 = first_object_3.author
        self.post_text_2 = first_object_3.text
        self.post_group_2 = first_object_3.group
        url = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user_1})
        ]
        cache.clear()
        for adress in url:
            response_4 = self.authorized_client.get(adress)
            first_object_4 = response_4.context['page_obj'][0]
            self.post_text_3 = first_object_4.text
            self.post_group_3 = first_object_4.group.title
        cache.clear()
        response_index = self.authorized_author.get(reverse('posts:index'))
        response_profile = self.authorized_author.get(
            reverse('posts:profile', kwargs={'username': self.user_1})
        )
        response_group_list = self.authorized_author.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.response_post_detail = (self.authorized_author.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post_id}))
        )
        self.responses = [
            response_index,
            response_profile,
            response_group_list,
        ]
        cache.clear()
        response_5 = self.authorized_author.get(reverse('posts:index'))
        self.content = response_5.content
        context = response_5.context['page_obj'][0]
        self.post_author_4 = context.author
        self.post_text_4 = context.text
        self.post_group_4 = context.group

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        self.assertTemplateUsed(self.response_8, self.template)

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        self.assertEqual(self.post_author_0, self.user_1)
        self.assertEqual(self.post_text_0, PostPagesTests.post.text)
        self.assertEqual(self.post_group_0, PostPagesTests.group)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        self.assertEqual(self.post_author_1, self.user_1)
        self.assertEqual(self.post_text_1, PostPagesTests.post.text)
        self.assertEqual(self.post_group_1, PostPagesTests.group)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        self.assertEqual(self.post_author_2, self.user_1)
        self.assertEqual(self.post_text_2, PostPagesTests.post.text)
        self.assertEqual(self.post_group_2, PostPagesTests.group)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post_id})
        )
        self.assertEqual(
            response.context['post_detail'].author, self.user_1
        )
        self.assertEqual(
            response.context['post_detail'].text, PostPagesTests.post.text
        )
        self.assertEqual(
            response.context['post_detail'].group, PostPagesTests.group
        )

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_author.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post_id})
        )
        for value, expected in self.form_fields_1.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        for value, expected in self.form_fields_2.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_show_on_index_group_profile_user(self):
        """
        Проверяем,что если при создании поста указать группу,
        то этот пост появляется:
        на главной странице сайта,
        на странице выбранной группы,
        в профайле пользователя.
        """
        self.assertEqual(self.post_text_3, self.post.text)
        self.assertEqual(self.post_group_3, self.post.group.title)

    def test_post_show_not_in_another_group(self):
        """
        Проверяем, что пост не попал в группу,
        для которой не был предназначен.
        """
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group_2.slug})
        )
        self.assertNotIn(
            self.post, response.context.get('page_obj').object_list
        )

    def test_post_with_a_image_show_correct_context(self):
        """
        Проверяем, что при выводе поста с картинкой
        изображение передаётся в словаре context на:
        Главную страницу,
        Страницу профайла,
        Страницу группы,
        Отдельную страницу поста.
        """
        for response in self.responses:
            with self.subTest(response=response):
                cache.clear()
                first_object = response.context['page_obj'][0]
                post_image_0 = first_object.image
                self.assertEqual(post_image_0, self.post.image)
        self.assertEqual(self.response_post_detail.context.get
                         ('post_detail').image, self.post.image
                         )

    def test_cache_index_page_correct_caching(self):
        """Кэш index сработает с кэшем."""
        self.assertEqual(self.post_author_4, self.user_1)
        self.assertEqual(self.post_text_4, PostPagesTests.post.text)
        self.assertEqual(self.post_group_4, PostPagesTests.group)
        post = Post.objects.get(id=self.post_id)
        post.delete()
        response_new = self.authorized_author.get(reverse('posts:index'))
        content_new = response_new.content
        self.assertEqual(self.content, content_new)
        cache.clear()
        response_new_2 = self.authorized_author.get(reverse('posts:index'))
        content_new_2 = response_new_2.content
        self.assertNotEqual(self.content, content_new_2)

    def test_following_authorized_user(self):
        """
        Проверка,что авторизованный пользователь
        может подписываться на других пользователей
        и удалять их из подписок.
        """
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.user_1})
        )
        follow = Follow.objects.get(author=self.user_1.id)
        follower = follow.user
        authorized_user = self.user_2
        self.assertEqual(follower, authorized_user)
        self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': self.user_1})
        )
        follow_2 = Follow.objects.filter(author=self.user_1.id).exists()
        self.assertFalse(follow_2)

    def test_new_post_create_in_follower_post_list(self):
        """
        Новая запись пользователя появляется
        в ленте тех, кто на него подписан
        и не появляется в ленте тех, кто не подписан.
        """
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.user_1})
        )
        response_6 = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn(
            self.post, response_6.context.get('page_obj').object_list
        )
        self.authorized_client_2.get(
            reverse('posts:profile_follow', kwargs={'username': self.user_2})
        )
        response_7 = self.authorized_client_2.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(
            self.post, response_7.context.get('page_obj').object_list
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Smirnov')
        cls.group = Group.objects.create(
            title='Тестовая группа title',
            slug='test-slug',
            description='Тестовое описание',
        )
        for i in range(13):
            post = 'cls.post_'
            post += str(i)
            post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()
        cache.clear()

    def test_index_first_page_contains_ten_records(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_three_records(self):
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_first_page_contains_ten_records(self):
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_second_page_contains_three_records(self):
        response = self.guest_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        response = self.guest_client.get(
            reverse('posts:profile',
                    kwargs={'username': PaginatorViewsTest.user})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_three_records(self):
        response = self.guest_client.get(
            reverse('posts:profile',
                    kwargs={'username': PaginatorViewsTest.user}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)
