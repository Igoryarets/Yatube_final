from django.core.cache import cache
from django.test import Client, TestCase
from posts.models import Group, Post, User


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(
            first_name='Leo',
            last_name='Messi',
            username='leomessi',
            email='leomessi@gmail.com'
        )

        cls.group = Group.objects.create(
            title='Group Leo',
            slug='leo',
            description='leomessi'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            pub_date='16.07.2021',
            author=PostsURLTests.user,
            group=PostsURLTests.group
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

        cache.clear()

        self.templates_url_names = {
            'index.html': '/',
            'group.html': '/group/leo/',
            'profile.html': '/leomessi/',
            'post.html': '/leomessi/1/',
        }

        self.url_new = '/new/'
        self.url_edit = '/leomessi/1/edit/'
        self.url_follow_index = '/follow/'
        self.url_follow = '/leomessi/follow/'
        self.url_unfollow = '/leomessi/unfollow/'
        self.url_comment = '/leomessi/1/comment/'

        self.template_new = 'new.html'
        self.template_edit = 'edit.html'
        self.template_follow_index = 'follow.html'

        self.redirect_guest = '/auth/login/?next=/new/'
        self.redirect_guest_follow_index = '/auth/login/?next=/follow/'
        self.redirect_guest_follow = '/auth/login/?next=/leomessi/follow/'
        self.redirect_follow = '/CR7/'
        self.redirect_comment_guest = '/auth/login/?next=/leomessi/1/comment/'

    def test_url_exists_at_desired_location_for_authorized_client(self):
        """
        Проверка доступности страниц для авторизованного
        пользователя.

        """
        for adress in self.templates_url_names.values():
            with self.subTest(adress=adress):
                response_authorized_client = self.authorized_client.get(adress)
                self.assertEqual(response_authorized_client.status_code, 200)

    def test_url_exists_at_desired_location_for_guest_client(self):
        """
        Проверка доступности страниц для неавторизованного
        пользователя.
        """
        for adress in self.templates_url_names.values():
            with self.subTest(adress=adress):
                response_guest_client = self.guest_client.get(adress)
                self.assertEqual(response_guest_client.status_code, 200)

    def test_urls_new_for_authorized_client(self):
        """
        Проверяем доступность страницы /new/
        для авторизованного пользователя.

        """
        response = self.authorized_client.get(self.url_new)
        self.assertEqual(response.status_code, 200)

    def test_urls_new_for_guest_client(self):
        """
        Проверяем доступность страницы /new/
        для неавторизованного пользователя.

        """
        response = self.guest_client.get(self.url_new)
        self.assertEqual(response.status_code, 302)

    def test_urls_follow_index_for_authorized_client(self):
        """
        Проверяем доступность страницы /follow/
        для авторизованного пользователя.

        """
        response = self.authorized_client.get(self.url_follow_index)
        self.assertEqual(response.status_code, 200)

    def test_urls_follow_index_for_guest_client(self):
        """
        Проверяем доступность страницы /follow/
        для неавторизованного пользователя.

        """
        response = self.guest_client.get(self.url_follow_index)
        self.assertEqual(response.status_code, 302)

    def test_urls_edit_for_authorized_client(self):
        """
        Проверяем доступность страницы /leomessi/1/edit/
        для авторизованного пользователя (автора поста).
        """
        response = self.authorized_client.get(self.url_edit)
        self.assertEqual(response.status_code, 200)

    def test_urls_edit_for_authorized_client(self):
        """
        Проверяем доступность страницы /leomessi/1/edit/
        для авторизованного пользователя (не автора поста).

        """
        user = User.objects.create(
            first_name='Cristiano',
            last_name='Ronaldo',
            username='CR7',
            email='CR7@gmail.com'
        )

        authorized_client = Client()
        authorized_client.force_login(user)

        response = authorized_client.get(self.url_edit)
        self.assertEqual(response.status_code, 302)

    def test_urls_edit_for_guest_client(self):
        """
        Проверяем доступность страницы /leomessi/1/edit/
        для анонимного пользователя.
        """
        response = self.guest_client.get(self.url_edit)
        self.assertEqual(response.status_code, 302)

    def test_urls_uses_correct_template_for_authorized_client(self):
        """
        Проверка имён вызываемых HTML-шаблонов
        для авторизованного пользователя.

        """
        for template, adress in self.templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_for_guest_client(self):
        """
        Проверка имён вызываемых HTML-шаблонов
        для неавторизованного пользователя.

        """
        for template, adress in self.templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_new_correct_template_for_authorized_client(self):
        """
        Проверка имени вызываемого HTML-шаблона /new/
        для авторизованного пользователя.

        """
        response = self.authorized_client.get(self.url_new)
        self.assertTemplateUsed(response, self.template_new)

    def test_urls_follow_index_correct_template_for_authorized_client(self):
        """
        Проверка имени вызываемого HTML-шаблона /follow/
        для авторизованного пользователя.

        """
        response = self.authorized_client.get(self.url_follow_index)
        self.assertTemplateUsed(response, self.template_follow_index)

    def test_urls_new_correct_redirect_for_guest_client(self):
        """
        Проверка попытки зайти на страницу создания нового
        поста незарегистрированным пользователем.

        """
        response = self.guest_client.get(self.url_new)
        self.assertRedirects(response, self.redirect_guest)

    def test_urls_follow_index_correct_redirect_for_guest_client(self):
        """
        Проверка попытки зайти на страницу follow.html
        незарегистрированным пользователем.

        """
        response = self.guest_client.get(self.url_follow_index)
        self.assertRedirects(response, self.redirect_guest_follow_index)

    def test_urls_edit_correct_template_for_authorized_client(self):
        """
        Проверка: какой шаблон вызывается для страницы
        редактирования поста /leomessi/1/edit/.

        """
        response = self.authorized_client.get(self.url_edit)
        self.assertTemplateUsed(response, self.template_edit)

    def test_urls_redirect_for_post_edit(self):
        """
        Проверка: правильно ли работает редирект
        со страницы /leomessi/1/edit/
        для тех, у кого нет прав доступа к этой странице.

        """
        user = User.objects.create(
            first_name='Cristiano',
            last_name='Ronaldo',
            username='CR7',
            email='CR7@gmail.com'
        )

        authorized_client = Client()
        authorized_client.force_login(user)

        response = authorized_client.get(self.url_edit)
        self.assertRedirects(response, self.templates_url_names['index.html'])

    def test_urls_redirect_for_follow_unfollow(self):
        """
        Проверка: правильно ли работает редирект
        со страницы /leomessi/follow/.

        """
        user = User.objects.create(
            first_name='Cristiano',
            last_name='Ronaldo',
            username='CR7',
            email='CR7@gmail.com'
        )

        authorized_client = Client()
        authorized_client.force_login(user)

        response = authorized_client.get(self.url_follow)
        self.assertRedirects(response, self.redirect_follow)

        response = authorized_client.get(self.url_unfollow)
        self.assertRedirects(response, self.redirect_follow)

    def test_urls_redirect_for_unfollow(self):
        """
        Проверка: правильно ли работает редирект
        со страницы /leomessi/unfollow/.

        """
        user = User.objects.create(
            first_name='Cristiano',
            last_name='Ronaldo',
            username='CR7',
            email='CR7@gmail.com'
        )
        authorized_client = Client()
        authorized_client.force_login(user)

        response = self.guest_client.get(self.url_follow)
        self.assertRedirects(response, self.redirect_guest_follow)

    def test_urls_redirect_for_comments(self):
        """
        Проверка: правильно ли работает редирект
        со страницы /leomessi/1/comment/.
        """
        response = self.guest_client.get(self.url_comment)
        self.assertRedirects(response, self.redirect_comment_guest)

        response = self.authorized_client.get(self.url_comment)
        self.assertRedirects(response, self.templates_url_names['post.html'])
