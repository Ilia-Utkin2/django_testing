from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client, form_data, news_detail_url):
    client.post(news_detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(
        author_client, news_detail_url, form_data, author, news):
    response = author_client.post(news_detail_url, data=form_data)
    assertRedirects(response, f'{news_detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(
        not_author_client, news_detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = not_author_client.post(news_detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
        author_client, delete_url, url_to_comments):
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_client, delete_url):
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        author_client, edit_url, new_form_data, comment, url_to_comments):
    response = author_client.post(edit_url, data=new_form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == new_form_data['text']


def test_user_cant_edit_comment_of_another_user(
        not_author_client, comment, edit_url, new_form_data, form_data):
    response = not_author_client.post(edit_url, data=new_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == form_data['text']
