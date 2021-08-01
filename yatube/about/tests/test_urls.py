from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

        self.templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }

    def test_about_url(self):

        for template, url_name in self.templates_url_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(url_name)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, 200)
