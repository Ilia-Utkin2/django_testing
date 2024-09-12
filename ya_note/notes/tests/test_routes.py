from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       author=cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.client_author = Client()
        cls.client_author.force_login(cls.author)
        cls.client_reader = Client()
        cls.client_reader.force_login(cls.reader)
        cls.url_detail = reverse('notes:detail', args=(cls.note.slug,))
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.url_list = reverse('notes:list')


    def test_pages_availability(self):
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_comment_edit_and_delete(self):
        users_statuses = (
            (self.client_author, HTTPStatus.OK),
            (self.client_reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for url in (self.url_detail, self.url_delete, self.url_edit):
                with self.subTest(user=user, url=url):
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for url in (
            self.url_edit,
            self.url_detail,
            self.url_delete,
            self.url_list
        ):
            with self.subTest(url=url):
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
