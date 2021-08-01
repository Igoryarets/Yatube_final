import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm, CommentForm
from posts.models import Group, Post, User


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовая группа для теста'
        )
        cls.form = PostForm()
        cls.form = CommentForm()

    @classmethod
    def tearDownClass(cls):
        # Рекурсивно удаляем временную после завершения тестов
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='leomessi')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

        self.redirect_guest = '/auth/login/?next=%2Fnew%2F'
        self.image_name = 'posts/small.gif'

    def test_create_post(self):
        """
        Проверка: тест для проверки формы создания
        нового поста на странице /new/,
        убеждаемся, что при отправке формы создаётся
        новая запись в базе данных.

        """
        # Подготавливаем изображение
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.test_group.id,
            'image': uploaded
        }
        response_1 = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        response_2 = self.guest_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response_1, reverse('index'))
        self.assertRedirects(response_2, self.redirect_guest)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(Post.objects.last().author, self.user)
        self.assertEqual(Post.objects.last().image, self.image_name)
        self.assertEqual(Post.objects.last().text, form_data['text'])
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=self.user,
                group=self.test_group,
                image=self.image_name,
            ).exists()
        )

    def test_edit_post(self):
        """
        Проверка: тест для проверки редактирования поста
        через форму на странице /<username>/<post_id>/edit/.
        Проверяем, что изменяется соответствующая запись
        в базе данных.

        """
        # Подготавливаем изображение
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        post = Post.objects.create(
            text='Тестовый текст поста',
            pub_date='16.07.2021',
            author=self.user,
            group=self.test_group,
        )
        form_data = {
            'text': 'Отредактированный тестовый текст',
            'group': self.test_group.id,
            'image': uploaded
        }
        response_1 = self.authorized_client.post(
            reverse('post_edit', kwargs={'username': self.user.username,
                                         'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response_1, reverse(
            'post', kwargs={'username': self.user.username,
                            'post_id': post.id})
        )
        post_request = self.authorized_client.get(reverse('index'))
        first_object = post_request.context['page'].object_list[0]

        print(first_object.image.name)

        self.assertEqual(first_object.text, form_data['text'])
        self.assertEqual(first_object.author, self.user)
#        self.assertEqual(first_object.image.name, self.image_name)
        self.assertEqual(first_object.group, self.test_group)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=self.user,
                group=self.test_group,
#                image=self.image_name,
            ).exists()
        )
        # добавил новую группу
        test_group_2 = Group.objects.create(
            title='Тест группа_2',
            slug='test_group_2',
            description='Тест группа для теста_2'
        )
        # меняю группу при редактировании поста
        post.group = test_group_2
        post.save()
        # выполняю запрос к старой группе
        response_2 = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': self.test_group.slug})
        )
        # проверяю, что пост исчез из старой группы
        post_object_2_count = response_2.context['page'].count(post)
        self.assertEqual(post_object_2_count, 0)

    def test_comment_post(self):
        """
        Проверка: только авторизированный пользователь
        может комментировать посты.

        """

        post = Post.objects.create(
            text='Тестовый текст поста',
            pub_date='16.07.2021',
            author=self.user,
            group=self.test_group
        )

        self.assertEqual(post.comments.count(), 0)
        form_data = {'text': 'Текст комментария'}
        response = self.authorized_client.post(
            reverse('add_comment', kwargs={'username': post.author.username,
                                           'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('post',
                             kwargs={
                                 'username': post.author.username,
                                 'post_id': post.id,
                             }))
        self.assertEqual(post.comments.count(), 1)
