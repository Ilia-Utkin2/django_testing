from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestHome(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.client_author = Client()
        cls.client_author.force_login(cls.author)
        cls.client_reader = Client()
        cls.client_reader.force_login(cls.reader)
        cls.url_add = reverse('notes:add')
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))

    def test_notes_list_for_different_users(self):
        users = (self.client_author, self.client_reader)
        for user in users:
            url = reverse('notes:list')
            response = user.get(url)
            object_list = response.context['object_list']
            if user is self.author:
                self.assertIn(self.note, object_list)
            elif user == self.reader:
                self.assertNotIn(self.note, object_list)

    def test_pages_contains_form(self):
        urls = (self.url_add, self.url_edit)

        for url in urls:
            response = self.client_author.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
