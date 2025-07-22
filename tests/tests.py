import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from courses.models import Course, Material
from users.models import User

from .models import Test, TestResult


@pytest.mark.django_db
def test_test_crud_and_check():
    teacher = User.objects.create_user(
        username='teacher', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='student', password='pass1234', role='student'
    )
    client = APIClient()
    client.force_authenticate(user=teacher)
    # Создание курса и материала
    course = Course.objects.create(title='Course', description='desc', owner=teacher)
    material = Material.objects.create(course=course, title='Mat', content='txt')
    # Создание теста
    test_url = reverse('test-list')
    test_resp = client.post(test_url, {'material': material.id, 'title': 'Test 1'})
    assert test_resp.status_code == 201
    test_id = test_resp.data['id']
    # Создание вопроса и ответов
    question_url = reverse('question-list')
    q_resp = client.post(question_url, {'test': test_id, 'text': '2+2?'})
    assert q_resp.status_code == 201
    q_id = q_resp.data['id']
    answer_url = reverse('answer-list')
    a1 = client.post(answer_url, {'question': q_id, 'text': '4', 'is_correct': True})
    a2 = client.post(answer_url, {'question': q_id, 'text': '5', 'is_correct': False})
    assert a1.status_code == 201 and a2.status_code == 201
    # Студент проходит тест
    client.force_authenticate(user=student)
    check_url = reverse('test-check', args=[test_id])
    answers = {str(q_id): a1.data['id']}
    resp = client.post(check_url, {'answers': answers}, format='json')
    assert resp.status_code == 200
    assert resp.data['score'] == 1.0
    # Проверка результата в базе
    assert TestResult.objects.filter(user=student, test_id=test_id).exists()


@pytest.mark.django_db
def test_student_cannot_create_test():
    student = User.objects.create_user(
        username='student2', password='pass1234', role='student'
    )
    client = APIClient()
    client.force_authenticate(user=student)
    url = reverse('test-list')
    resp = client.post(url, {'material': 1, 'title': 'Should fail'})
    assert resp.status_code == 403


@pytest.mark.django_db
def test_unauthorized_access_to_tests():
    url = reverse('test-list')
    client = APIClient()
    resp = client.get(url)
    assert resp.status_code == 401


@pytest.mark.django_db
def test_get_nonexistent_test():
    teacher = User.objects.create_user(
        username='teacherX', password='pass1234', role='teacher'
    )
    client = APIClient()
    client.force_authenticate(user=teacher)
    url = reverse('test-detail', args=[9999])
    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.django_db
def test_check_test_with_invalid_data():
    teacher = User.objects.create_user(
        username='teacherY', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='studentY', password='pass1234', role='student'
    )
    client = APIClient()
    client.force_authenticate(user=teacher)
    course = Course.objects.create(title='CourseY', description='desc', owner=teacher)
    material = Material.objects.create(course=course, title='MatY', content='txt')
    test = Test.objects.create(material=material, title='TestY')
    client.force_authenticate(user=student)
    check_url = reverse('test-check', args=[test.id])
    # Пустые ответы
    resp = client.post(check_url, {'answers': {}}, format='json')
    assert resp.status_code == 200
    # Некорректные ответы
    resp = client.post(check_url, {'answers': {'999': 999}}, format='json')
    assert resp.status_code == 200
