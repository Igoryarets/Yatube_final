from django.test import TestCase
from posts.models import Comment, Follow, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(
            first_name='Leo',
            last_name='Messi',
            username='leomessi',
            email='leomessi@gmail.com'
        )
        cls.user_following = User.objects.create(
            first_name='Cristiano',
            last_name='Ronaldo',
            username='CR7',
            email='CR7@gmail.com'
        )

        cls.group = Group.objects.create(
            title='Group Leo',
            slug='leo',
            description='leomessi'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            pub_date='16.07.2021',
            author=PostModelTest.user,
            group=PostModelTest.group
        )

        cls.comment = Comment.objects.create(
            post=PostModelTest.post,
            author=PostModelTest.user,
            text='Рандомный комментарий',
        )

        cls.follow = Follow.objects.create(
            user=PostModelTest.user,
            author=PostModelTest.user_following,
        )

    def test_object_name_is_title_field(self):
        """
        Проверка: правильно ли отображается значение поля __str__
        в объектах моделей Post и Group.

        """

        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

        group = PostModelTest.group
        expected_object_name = group.title[:15]
        self.assertEqual(expected_object_name, str(group))

        comment = PostModelTest.comment
        expected_object_name = comment.text
        self.assertEqual(expected_object_name, str(comment))
