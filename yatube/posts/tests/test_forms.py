import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.shortcuts import get_object_or_404
from django.urls import reverse

from posts.forms import PostForm, CommentForm
from ..models import Group, Post, Comment, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='Smirnov')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )
        cls.form_1 = PostForm()
        cls.form_2 = CommentForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=False)

    def setUp(self):
        self.post_id = PostCreateFormTests.post.id
        self.post_3 = Post.objects.get(id=self.post_id)
        self.posts_count = Post.objects.count()
        self.authorized_author = Client()
        self.authorized_author.force_login(PostCreateFormTests.user)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded_1 = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data_1 = {
            'text': 'Тестовый текст',
            'group': PostCreateFormTests.group.id,
            'image': uploaded_1,
        }
        self.response_1 = self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data_1,
            follow=True
        )
        big_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded_2 = SimpleUploadedFile(
            name='big.gif',
            content=big_gif,
            content_type='image/gif'
        )
        form_data_2 = {
            'text': 'Отредактированный текст',
            'image': uploaded_2,
        }

        self.response_2 = self.authorized_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post_id}),
            data=form_data_2,
            follow=True
        )
        self.assertRedirects(self.response_2, reverse('posts:post_detail',
                             kwargs={'post_id': self.post_id})
                             )
        post_1 = Post.objects.get(id=self.post_id)
        self.post_text = PostCreateFormTests.post.text
        self.post_image = self.post.image
        self.post_text_new = post_1.text
        self.post_id_new = post_1.id
        self.post_image_new = post_1.image
        form_data_3 = {'text': 'Первый комментарий'}
        self.response_3 = self.authorized_author.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data_3,
            follow=True
        )
        post_2 = get_object_or_404(Post, id=self.post.id)
        self.comments = post_2.comments.get()

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        self.assertEqual(Post.objects.count(), self.posts_count + 1)
        self.assertRedirects(self.response_1, reverse('posts:profile',
                             kwargs={'username': PostCreateFormTests.user})
                             )
        self.assertTrue(
            Post.objects.filter(
                text=self.post_3.text,
                group=self.post_3.group,
                image=self.post_3.image
            ).exists()
        )

    def test_post_edit(self):
        """
        При редактировании поста происходит
        изменение поста в базе данных.
        При отправке поста с картинкой
        через форму PostForm создаётся
        запись в базе данных.
        """
        self.assertNotEqual(self.post_text, self.post_text_new)
        self.assertNotEqual(self.post_image, self.post_image_new)
        self.assertEqual(self.post_id, self.post_id_new)

    def test_add_commen(self):
        """
        После успешной отправки
        комментарий появляется на странице поста.
        """
        self.assertRedirects(self.response_3, reverse('posts:post_detail',
                             kwargs={'post_id': self.post.id})
                             )
        self.assertTrue(Comment.objects.filter(id=self.comments.id).exists())
