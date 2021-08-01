import shutil

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms

from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(
            first_name='Leo',
            last_name='Messi',
            username='leomessi',
            email='leomessi@gmail.com'
        )

        cls.follower = User.objects.create(
            username='follower',
        )

        cls.group = Group.objects.create(
            title='Group Leo',
            slug='leo',
            description='leomessi'
        )
        # Подготавливаем изображение
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            pub_date='16.07.2021',
            author=PostViewsTest.user,
            group=PostViewsTest.group,
            image=PostViewsTest.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Рекурсивно удаляем временную после завершения тестов
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        # Создаем авторизованного подписчика
        self.follower_client = Client()
        # Авторизуем подписчика
        self.follower_client.force_login(self.follower)

        cache.clear()

        # словарь пары "имя_html_шаблона: name" для метода
        # test_page_uses_correct_template
        self.templates_page_names = {
            'index.html': reverse('index'),
            'new.html': reverse('new_post'),
            'group.html': reverse(
                'group_posts', kwargs={'slug': self.group.slug}
            ),
            'follow.html': reverse('follow_index')
        }
        # словарь для проверки правильного контекста (form)
        # для методов new_post, post_edit
        self.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        # словарь пары "имя_html_шаблона: name" для проверки паджинатора
        self.templates_page_names_for_paginator = {
            'index.html': reverse('index'),
            'profile.html': reverse(
                'profile', kwargs={'username': self.user.username}
            ),
            'group.html': reverse(
                'group_posts', kwargs={'slug': self.group.slug}
            ),
            'follow.html': reverse('follow_index')
        }
        # словарь пары "имя_html_шаблона: name" для
        # метода test_create_title_group_in_new_post
        self.templates_page_names_for_new_post = {
            'index.html': reverse('index'),
            'group.html': reverse(
                'group_posts', kwargs={'slug': self.group.slug}
            )
        }

    def test_page_uses_correct_template(self):
        """
        Проверка: view-функции используют ожидаемые HTML-шаблоны.

        """
        for template, reverse_name in self.templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_shows_correct_context_for_index(self):
        """
        Проверка: в шаблон передан правильный контекст
        в шаблон передан правильный контекст (page) для функции index.

        """
        response = self.authorized_client.get(reverse('index'))
        first_object = response.context['page'].object_list[0]

        self.assertEqual(str(first_object.author), self.user.username)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.pub_date, self.post.pub_date)
        self.assertEqual(first_object.group, self.post.group)
        self.assertEqual(first_object.image, self.post.image)

    def test_shows_correct_context_for_group_posts(self):
        """
        Проверка: в шаблон передан правильный контекст (group, page)
        для метода group_posts.

        """
        response = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': self.group.slug})
        )

        first_object = response.context['group']
        second_object = response.context['page'].object_list[0]

        self.assertEqual(first_object.title, self.group.title)
        self.assertEqual(first_object.slug, self.group.slug)
        self.assertEqual(first_object.description, self.group.description)
        self.assertEqual(str(second_object.author), self.user.username)
        self.assertEqual(second_object.text, self.post.text)
        self.assertEqual(second_object.image, self.post.image)

    def test_shows_correct_context_for_new_post(self):
        """
        Проверка: в шаблон передан правильный контекст (form)
        для метода new_post.

        """
        response = self.authorized_client.get(reverse('new_post'))

        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_shows_correct_context_for_post_edit(self):
        """
        Проверка: в шаблон передан правильный контекст (author, post, form)
        для метода post_edit.

        """
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={'username': 'leomessi', 'post_id': 1})
        )

        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

        author_object = response.context['author']
        self.assertEqual(str(author_object), self.user.username)

        post_object = response.context['post']
        self.assertEqual(str(post_object), self.post.text[:15])

    def test_shows_correct_context_for_profile(self):
        """
        Проверка: в шаблон передан правильный контекст
        (author, count, page, following) для метода profile.

        """
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.user.username})
        )
        author_object = response.context['author']
        self.assertEqual(str(author_object), self.user.username)

        post_object = response.context['page'].object_list[0]
        self.assertEqual(str(post_object), self.post.text[:15])
        self.assertEqual(post_object.image, self.post.image)

        count_object = response.context['count']
        self.assertEqual(str(count_object), '1')

        # подписка на автора поста
        self.follower_client.get(
            reverse('profile_follow', kwargs={'username': self.post.author})
        )
        # переходим в профайл follower_client
        response_follow = self.follower_client.get(
            reverse('profile', kwargs={'username': self.user.username})
        )
        # проверяем правильность переданного в контекст
        # значения переменной following
        follow_object = response_follow.context['following']
        self.assertEqual(follow_object, True)

        # одписка на автора поста
        self.follower_client.get(
            reverse('profile_unfollow', kwargs={'username': self.post.author})
        )
        # переходим в профайл follower_client
        response_unfollow = self.follower_client.get(
            reverse('profile', kwargs={'username': self.user.username})
        )
        # проверяем правильность переданного в контекст
        # значения переменной following
        follow_object = response_unfollow.context['following']
        self.assertEqual(follow_object, False)

    def test_shows_correct_context_for_post_view(self):
        """
        Проверка: в шаблон передан правильный контекст
        (author, count, post, form, comments, following)
        для метода post_view.

        """
        response = self.authorized_client.get(
            reverse(
                'post', kwargs={'username': 'leomessi',
                                'post_id': self.post.id}
            )
        )
        author_object = response.context['author']
        self.assertEqual(str(author_object), self.user.username)

        post_object = response.context['post']
        self.assertEqual(str(post_object), self.post.text[:15])
        self.assertEqual(post_object.image, self.post.image)

        count_object = response.context['count']
        self.assertEqual(str(count_object), '1')

        # подписка на автора поста
        self.follower_client.get(
            reverse('profile_follow', kwargs={'username': self.post.author})
        )
        # переходим в на страницу поста пользователя follower_client
        response_follow = self.follower_client.get(
            reverse('post', kwargs={'username': self.post.author,
                                    'post_id': self.post.id})
        )
        # проверяем правильность переданного в контекст
        # значения переменной following
        follow_object = response_follow.context['following']
        self.assertEqual(follow_object, True)

        # одписка на автора поста
        self.follower_client.get(
            reverse('profile_unfollow', kwargs={'username': self.post.author})
        )
        # переходим в на страницу поста пользователя follower_client
        response_unfollow = self.follower_client.get(
            reverse('post', kwargs={'username': self.post.author,
                                    'post_id': self.post.id})
        )
        # проверяем правильность переданного в контекст
        # значения переменной following
        follow_object = response_unfollow.context['following']
        self.assertEqual(follow_object, False)

        # проверяем правильность переданного в контекст значения comments
        form_data = {'text': 'Текст комментария'}
        self.authorized_client.post(
            reverse('add_comment',
                    kwargs={'username': self.post.author.username,
                            'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        response = self.authorized_client.get(
            reverse(
                'post', kwargs={'username': 'leomessi',
                                'post_id': self.post.id}
            )
        )
        self.assertEqual(
            str(response.context['comments'][0]), form_data['text']
        )

    def test_first_page_contains_ten_records(self):
        """
        Проверка паджинатора.

        """
        for record in range(0, 13):
            Post.objects.create(
                text=f'Тестовый текст поста: запись {record}',
                pub_date='16.07.2021',
                author=PostViewsTest.user,
                group=PostViewsTest.group,
                image=PostViewsTest.uploaded,
            )

        self.follower_client.get(
            reverse('profile_follow', kwargs={'username': self.post.author})
        )

        for reverse_name in self.templates_page_names_for_paginator.values():
            with self.subTest(reverse_name=reverse_name):
                response = self.follower_client.get(reverse_name)
                record_page = len(response.context['page'].object_list)
                self.assertEqual(record_page, 10)

    def test_create_title_group_in_new_post(self):
        """
        Проверка: если мы указали группу при создании поста,
        то этот пост появится на главной странице и на странице
        этой группы.

        """
        for reverse_name in self.templates_page_names_for_new_post.values():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                post_object = response.context['page'].object_list[0]
                self.assertEqual(str(post_object), self.post.text[:15])

    def test_title_group_in_new_post_for_other_group(self):
        """
        Проверка:  пост не попадает в группу, для которой
        не был предназначен.

        """
        other_group = Group.objects.create(
            title='Football',
            slug='football',
            description='football in the world'
        )
        Post.objects.create(
            text='Футбольный текст поста',
            pub_date='18.07.2021',
            author=PostViewsTest.user,
            group=other_group,
            image=PostViewsTest.uploaded,
        )

        response_1 = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': self.group.slug})
        )
        post_object_1 = response_1.context['page'].object_list[0]

        response_2 = self.authorized_client.get(
            reverse('group_posts', kwargs={'slug': other_group.slug})
        )
        post_object_2 = response_2.context['page'].object_list[0]

        self.assertNotEqual(post_object_1, post_object_2)

    def test_cache(self):
        """
        Проверка кеширования главной страницы.

        """
        response_content = self.authorized_client.get(reverse('index')).content
        Post.objects.create(
            text='Футбольный текст поста',
            pub_date='29.07.2021',
            author=PostViewsTest.user,
            group=PostViewsTest.group,
            image=PostViewsTest.uploaded,
        )
        response_content_1 = self.authorized_client.get(
            reverse('index')
        ).content
        self.assertEqual(response_content, response_content_1)
        cache.clear()
        response_content_2 = self.authorized_client.get(
            reverse('index')
        ).content
        self.assertNotEqual(response_content_1, response_content_2)

    def test_following_post(self):
        """
        Проверка системы подписки и отписки
        на авторов постов.

        """
        # проверяем, что follower_client еще не подписан на автора поста
        response_1 = self.follower_client.get(reverse('follow_index'))
        page_object_1 = response_1.context['page'].object_list
        self.assertEqual((len(page_object_1)), 0)

        # подписываемся на автора поста
        self.follower_client.get(
            reverse('profile_follow', kwargs={'username': self.post.author})
        )

        # проверяем, что follower_client подписался
        response_2 = self.follower_client.get(reverse('follow_index'))
        page_object_2 = response_2.context['page'].object_list
        self.assertEqual((len(page_object_2)), 1)

        #  проверяем, что в шаблон follow.html передан правильный контекст
        page_object_2 = response_2.context['page'].object_list[0]
        self.assertEqual((page_object_2.author), self.post.author)
        self.assertEqual((page_object_2.text), self.post.text)
        self.assertEqual((page_object_2.pub_date), self.post.pub_date)
        self.assertEqual((page_object_2.group), self.post.group)
        self.assertEqual((page_object_2.image), self.post.image)

        # отписываемся от автора поста
        self.follower_client.get(reverse('profile_unfollow',
                                 kwargs={'username': self.post.author}))

        # проверяем, что follower_client отписался
        response_3 = self.follower_client.get(reverse('follow_index'))
        page_object_3 = response_3.context['page'].object_list
        self.assertEqual((len(page_object_3)), 0)

        # проверяем, что автор не может подписаться сам на себя
        response_4 = self.authorized_client.get(reverse('follow_index'))
        page_object_4 = response_4.context['page'].object_list
        self.assertEqual((len(page_object_4)), 0)
        self.authorized_client.get(
            reverse('profile_follow', kwargs={'username': self.post.author})
        )
        response_5 = self.authorized_client.get(reverse('follow_index'))
        page_object_5 = response_5.context['page'].object_list
        self.assertEqual((len(page_object_5)), 0)
