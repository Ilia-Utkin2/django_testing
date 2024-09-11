from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.author = User.objects.create(username='Лев Толстой')
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        cls.client_author = Client()
        cls.client_author.force_login(cls.author)

    def test_user_can_create_note(self):
        url = reverse('notes:add')
        response = self.client_author.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_empty_slug(self):
        url = reverse('notes:add')
        self.form_data.pop('slug')

        response = self.client_author.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        new_note = Note.objects.get()
        self.assertEqual(new_note.slug, slugify(self.form_data['title']))


class TestNoteEditDelete(TestCase):
    TITLE = 'Заголовок'
    TEXT = 'Текст'
    SLUG = 'slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Читатель')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(title=cls.TITLE,
                                       text=cls.TEXT,
                                       slug=cls.SLUG,
                                       author=cls.author)
        cls.url_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.new_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_delete_note_author(self):
        response = self.author_client.delete(self.url_delete)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_delete_note_reader(self):
        response = self.reader_client.delete(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_edit_note_author(self):
        response = self.author_client.post(self.url_edit, data=self.new_data)
        self.assertRedirects(response, reverse('notes:success'))
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, self.new_data['title'])
        self.assertEqual(note_from_db.text, self.new_data['text'])
        self.assertEqual(note_from_db.slug, self.new_data['slug'])

    def test_edit_note_reader(self):
        response = self.reader_client.post(self.url_edit, data=self.new_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(self.note.title, self.TITLE)
        self.assertEqual(self.note.text, self.TEXT)
        self.assertEqual(self.note.slug, self.SLUG)
