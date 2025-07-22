from unittest import mock

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from .models import User


@pytest.mark.django_db
def test_user_registration():
    client = APIClient()
    url = reverse('register')
    data = {
        'username': 'student1',
        'password': 'pass1234',
        'email': 'student1@example.com',
    }
    with mock.patch('users.tasks.send_confirmation_email.delay') as mocked_task:
        response = client.post(url, data)
        assert response.status_code == 201
        user = User.objects.get(username='student1')
        assert not user.email_confirmed
        assert mocked_task.called
        assert mocked_task.call_args[0][0] == 'student1@example.com'
        assert str(user.email_confirmation_token) in mocked_task.call_args[0][1]


@pytest.mark.django_db
def test_user_login():
    user = User.objects.create_user(username='student2', password='pass1234')
    client = APIClient()
    url = reverse('token_obtain_pair')
    data = {'username': 'student2', 'password': 'pass1234'}
    response = client.post(url, data)
    assert response.status_code == 200
    assert 'access' in response.data


@pytest.mark.django_db
def test_user_permissions():
    admin = User.objects.create_user(
        username='admin', password='adminpass', role='admin'
    )
    student = User.objects.create_user(
        username='student', password='studentpass', role='student'
    )
    client = APIClient()
    # Only admin can list users
    url = reverse('user-list')
    client.force_authenticate(user=student)
    response = client.get(url)
    assert response.status_code == 403
    client.force_authenticate(user=admin)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_unauthorized_access():
    client = APIClient()
    url = reverse('user-list')
    response = client.get(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_registration_empty_fields():
    client = APIClient()
    url = reverse('register')
    data = {'username': '', 'password': '', 'email': ''}
    response = client.post(url, data)
    assert response.status_code == 400


@pytest.mark.django_db
def test_sql_injection_registration():
    client = APIClient()
    url = reverse('register')
    data = {'username': "' OR 1=1; --", 'password': 'pass', 'email': 'a@a.a'}
    response = client.post(url, data)
    assert response.status_code in (400, 201)
    # Проверяем, что не произошло массового создания пользователей
    assert User.objects.filter(username="' OR 1=1; --").count() <= 1


@pytest.mark.django_db
def test_email_confirmation():
    user = User.objects.create_user(
        username='student2', password='pass1234', email='student2@example.com'
    )
    user.email_confirmed = False
    user.save()
    client = APIClient()
    url = reverse('confirm-email', args=[user.email_confirmation_token])
    response = client.get(url)
    user.refresh_from_db()
    assert response.status_code == 200
    assert user.email_confirmed


@pytest.mark.django_db
def test_email_confirmation_repeat():
    user = User.objects.create_user(
        username='student3',
        password='pass1234',
        email='student3@example.com',
        email_confirmed=True,
    )
    client = APIClient()
    url = reverse('confirm-email', args=[user.email_confirmation_token])
    response = client.get(url)
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.email_confirmed


@pytest.mark.django_db
def test_email_confirmation_invalid_token():
    client = APIClient()
    import uuid

    url = reverse('confirm-email', args=[uuid.uuid4()])
    response = client.get(url)
    assert response.status_code == 404
