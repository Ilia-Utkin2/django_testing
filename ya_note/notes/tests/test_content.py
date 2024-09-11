from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestHome(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       author=cls.author)
        cls.reader = User.objects.create(username='Читатель простой')

    def test_notes_list_for_different_users(self):
        users = (self.author, self.reader)
        for user in users:
            self.client.force_login(user)
            url = reverse('notes:list')
            response = self.client.get(url)
            object_list = response.context['object_list']
            if user == self.author:
                self.assertIn(self.note, object_list)

            elif user == self.reader:
                self.assertNotIn(self.note, object_list)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in urls:
            urls = reverse(name, args=args)
            self.client.force_login(self.author)

            response = self.client.get(urls)
            self.assertIn('form', response.context)

            self.assertIsInstance(response.context['form'], NoteForm)
