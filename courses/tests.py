import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from users.models import User

from .models import Course


@pytest.mark.django_db
def test_course_create_by_teacher():
    teacher = User.objects.create_user(
        username='teacher1', password='pass1234', role='teacher'
    )
    client = APIClient()
    client.force_authenticate(user=teacher)
    url = reverse('course-list')
    data = {'title': 'Course 1', 'description': 'desc'}
    response = client.post(url, data)
    assert response.status_code == 201
    assert Course.objects.filter(title='Course 1').exists()


@pytest.mark.django_db
def test_course_create_by_student_forbidden():
    student = User.objects.create_user(
        username='student1', password='pass1234', role='student'
    )
    client = APIClient()
    client.force_authenticate(user=student)
    url = reverse('course-list')
    data = {'title': 'Course 2', 'description': 'desc'}
    response = client.post(url, data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_material_crud():
    teacher = User.objects.create_user(
        username='teacher2', password='pass1234', role='teacher'
    )
    client = APIClient()
    client.force_authenticate(user=teacher)
    course = Course.objects.create(title='Course X', description='desc', owner=teacher)
    url = reverse('material-list')
    data = {'course': course.id, 'title': 'Material 1', 'content': 'text'}
    response = client.post(url, data)
    assert response.status_code == 201
    material_id = response.data['id']
    # Read
    response = client.get(reverse('material-detail', args=[material_id]))
    assert response.status_code == 200
    # Update
    response = client.patch(
        reverse('material-detail', args=[material_id]),
        {'title': 'Updated'},
        format='json',
    )
    assert response.status_code == 200
    # Delete
    response = client.delete(reverse('material-detail', args=[material_id]))
    assert response.status_code == 204


@pytest.mark.django_db
def test_course_search_and_ordering():
    teacher = User.objects.create_user(
        username='teacher3', password='pass1234', role='teacher'
    )
    client = APIClient()
    client.force_authenticate(user=teacher)
    Course.objects.create(title='Python', description='prog', owner=teacher)
    Course.objects.create(title='Django', description='web', owner=teacher)
    url = reverse('course-list')
    # Поиск
    response = client.get(url + '?search=Python')
    assert response.status_code == 200
    assert any('Python' in c['title'] for c in response.data['results'])
    # Сортировка
    response = client.get(url + '?ordering=title')
    assert response.status_code == 200
    titles = [c['title'] for c in response.data['results']]
    assert titles == sorted(titles)


@pytest.mark.django_db
def test_course_create_unauthorized():
    client = APIClient()
    url = reverse('course-list')
    data = {'title': 'Course 3', 'description': 'desc'}
    response = client.post(url, data)
    assert response.status_code == 401


@pytest.mark.django_db
def test_student_cannot_update_foreign_course():
    teacher = User.objects.create_user(
        username='teacher4', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='student2', password='pass1234', role='student'
    )
    course = Course.objects.create(title='Foreign', description='desc', owner=teacher)
    client = APIClient()
    client.force_authenticate(user=student)
    url = reverse('course-detail', args=[course.id])
    response = client.patch(url, {'title': 'Hacked'}, format='json')
    assert response.status_code in (403, 404)


@pytest.mark.django_db
def test_get_nonexistent_course():
    teacher = User.objects.create_user(
        username='teacher5', password='pass1234', role='teacher'
    )
    client = APIClient()
    client.force_authenticate(user=teacher)
    url = reverse('course-detail', args=[9999])
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_mass_assignment_owner():
    teacher = User.objects.create_user(
        username='teacher6', password='pass1234', role='teacher'
    )
    other = User.objects.create_user(
        username='other', password='pass1234', role='teacher'
    )
    client = APIClient()
    client.force_authenticate(user=teacher)
    url = reverse('course-list')
    data = {'title': 'MassAssign', 'description': 'desc', 'owner': other.id}
    response = client.post(url, data)
    assert response.status_code == 201
    course = Course.objects.get(title='MassAssign')
    assert course.owner == teacher
