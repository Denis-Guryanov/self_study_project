import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from users.models import User

from .models import Course, Material, Comment, UserActivity, Recommendation
from .services import RecommendationService, ActivityService


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


# Новые тесты для комментариев
@pytest.mark.django_db
def test_comment_create():
    teacher = User.objects.create_user(
        username='teacher7', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='student3', password='pass1234', role='student'
    )
    course = Course.objects.create(title='Course Y', description='desc', owner=teacher)
    material = Material.objects.create(
        title='Material Y', content='content', course=course, owner=teacher
    )
    
    client = APIClient()
    client.force_authenticate(user=student)
    url = reverse('comment-list')
    data = {
        'material': material.id,
        'content': 'Great material!',
    }
    response = client.post(url, data)
    assert response.status_code == 201
    assert Comment.objects.filter(content='Great material!').exists()
    comment = Comment.objects.get(content='Great material!')
    assert comment.user == student
    assert not comment.is_approved


@pytest.mark.django_db
def test_comment_reply():
    teacher = User.objects.create_user(
        username='teacher8', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='student4', password='pass1234', role='student'
    )
    course = Course.objects.create(title='Course Z', description='desc', owner=teacher)
    material = Material.objects.create(
        title='Material Z', content='content', course=course, owner=teacher
    )
    parent_comment = Comment.objects.create(
        material=material, user=student, content='Parent comment'
    )
    
    client = APIClient()
    client.force_authenticate(user=teacher)
    url = reverse('comment-list')
    data = {
        'material': material.id,
        'content': 'Reply to comment',
        'parent': parent_comment.id,
    }
    response = client.post(url, data)
    assert response.status_code == 201
    reply = Comment.objects.get(content='Reply to comment')
    assert reply.parent == parent_comment


@pytest.mark.django_db
def test_comment_approve():
    teacher = User.objects.create_user(
        username='teacher9', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='student5', password='pass1234', role='student'
    )
    course = Course.objects.create(title='Course W', description='desc', owner=teacher)
    material = Material.objects.create(
        title='Material W', content='content', course=course, owner=teacher
    )
    comment = Comment.objects.create(
        material=material, user=student, content='Comment to approve'
    )
    
    client = APIClient()
    client.force_authenticate(user=teacher)
    url = reverse('comment-approve', args=[comment.id])
    response = client.post(url)
    assert response.status_code == 200
    comment.refresh_from_db()
    assert comment.is_approved


@pytest.mark.django_db
def test_comment_approve_student_forbidden():
    teacher = User.objects.create_user(
        username='teacher10', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='student6', password='pass1234', role='student'
    )
    course = Course.objects.create(title='Course V', description='desc', owner=teacher)
    material = Material.objects.create(
        title='Material V', content='content', course=course, owner=teacher
    )
    comment = Comment.objects.create(
        material=material, user=student, content='Comment to approve'
    )
    
    client = APIClient()
    client.force_authenticate(user=student)
    url = reverse('comment-approve', args=[comment.id])
    response = client.post(url)
    assert response.status_code == 403


# Тесты для новых полей курсов
@pytest.mark.django_db
def test_course_with_tags_and_difficulty():
    teacher = User.objects.create_user(
        username='teacher11', password='pass1234', role='teacher'
    )
    client = APIClient()
    client.force_authenticate(user=teacher)
    url = reverse('course-list')
    data = {
        'title': 'Advanced Python',
        'description': 'Advanced Python course',
        'tags': '["python", "advanced", "programming"]',
        'difficulty': 'advanced'
    }
    response = client.post(url, data)
    assert response.status_code == 201
    course = Course.objects.get(title='Advanced Python')
    assert course.tags == ['python', 'advanced', 'programming']
    assert course.difficulty == 'advanced'


@pytest.mark.django_db
def test_course_difficulty_choices():
    teacher = User.objects.create_user(
        username='teacher12', password='pass1234', role='teacher'
    )
    client = APIClient()
    client.force_authenticate(user=teacher)
    url = reverse('course-list')
    
    # Тест валидных значений
    valid_difficulties = ['beginner', 'intermediate', 'advanced']
    for difficulty in valid_difficulties:
        data = {
            'title': f'Course {difficulty}',
            'description': 'desc',
            'difficulty': difficulty
        }
        response = client.post(url, data)
        assert response.status_code == 201
    
    # Тест невалидного значения - Django не валидирует choices на уровне API
    # поэтому этот тест может проходить, но мы можем проверить на уровне модели
    data = {
        'title': 'Invalid Course',
        'description': 'desc',
        'difficulty': 'invalid'
    }
    response = client.post(url, data)
    # Django может принять невалидное значение, но мы можем проверить на уровне модели
    if response.status_code == 201:
        # Если API принял, проверим что в базе данных значение корректное
        course = Course.objects.get(title='Invalid Course')
        assert course.difficulty in ['beginner', 'intermediate', 'advanced']
    else:
        assert response.status_code == 400


# Тесты для сервиса рекомендаций
@pytest.mark.django_db
def test_recommendation_service():
    teacher = User.objects.create_user(
        username='teacher13', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='student7', password='pass1234', role='student'
    )
    
    # Создаем курсы с тегами
    course1 = Course.objects.create(
        title='Python Basics',
        description='Basic Python course',
        owner=teacher,
        tags=['python', 'basics'],
        difficulty='beginner'
    )
    course2 = Course.objects.create(
        title='Python Advanced',
        description='Advanced Python course',
        owner=teacher,
        tags=['python', 'advanced'],
        difficulty='advanced'
    )
    course3 = Course.objects.create(
        title='Django Web',
        description='Django web development',
        owner=teacher,
        tags=['django', 'web'],
        difficulty='intermediate'
    )
    
    # Создаем активность пользователя
    UserActivity.objects.create(
        user=student,
        course=course1,
        activity_type='complete',
        score=85.0
    )
    
    # Генерируем рекомендации
    recommendations = RecommendationService.generate_recommendations(student, limit=3)
    
    assert len(recommendations) > 0
    # Проверяем, что рекомендации отсортированы по score
    scores = [r.score for r in recommendations]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.django_db
def test_activity_service():
    teacher = User.objects.create_user(
        username='teacher14', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='student8', password='pass1234', role='student'
    )
    course = Course.objects.create(
        title='Test Course',
        description='Test course',
        owner=teacher,
        tags=['test'],
        difficulty='beginner'
    )
    
    # Тестируем отслеживание активности
    ActivityService.track_activity(student, course, 'view')
    ActivityService.track_activity(student, course, 'complete', score=90.0)
    ActivityService.track_activity(student, course, 'test_passed', score=85.0)
    
    # Проверяем, что активности созданы
    activities = UserActivity.objects.filter(user=student, course=course)
    assert activities.count() == 3
    
    # Проверяем прогресс пользователя
    progress = ActivityService.get_user_progress(student)
    assert progress['courses_viewed'] == 1
    assert progress['courses_completed'] == 1
    assert progress['tests_passed'] == 1
    assert progress['avg_score'] == 87.5
    assert progress['total_activities'] == 3


@pytest.mark.django_db
def test_user_preferences_analysis():
    teacher = User.objects.create_user(
        username='teacher15', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='student9', password='pass1234', role='student'
    )
    
    # Создаем курсы с разными тегами и сложностью
    course1 = Course.objects.create(
        title='Python Course',
        owner=teacher,
        tags=['python', 'programming'],
        difficulty='beginner'
    )
    course2 = Course.objects.create(
        title='Django Course',
        owner=teacher,
        tags=['django', 'web'],
        difficulty='intermediate'
    )
    
    # Создаем активность
    UserActivity.objects.create(
        user=student,
        course=course1,
        activity_type='complete',
        score=80.0
    )
    UserActivity.objects.create(
        user=student,
        course=course2,
        activity_type='complete',
        score=85.0
    )
    
    # Анализируем предпочтения
    preferences = RecommendationService.get_user_preferences(student)
    
    assert 'python' in preferences['tags']
    assert 'django' in preferences['tags']
    assert 'beginner' in preferences['difficulty']
    assert 'intermediate' in preferences['difficulty']
    assert preferences['avg_score'] == 82.5


@pytest.mark.django_db
def test_course_score_calculation():
    teacher = User.objects.create_user(
        username='teacher16', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='student10', password='pass1234', role='student'
    )
    
    # Создаем курс, который пользователь уже проходил
    course1 = Course.objects.create(
        title='Python Course',
        owner=teacher,
        tags=['python'],
        difficulty='beginner'
    )
    
    # Создаем новый курс для рекомендации
    course2 = Course.objects.create(
        title='Advanced Python',
        owner=teacher,
        tags=['python', 'advanced'],
        difficulty='intermediate'
    )
    
    # Создаем активность по первому курсу
    UserActivity.objects.create(
        user=student,
        course=course1,
        activity_type='complete',
        score=85.0
    )
    
    # Рассчитываем score для второго курса
    score = RecommendationService.calculate_course_score(student, course2)
    
    assert 0 <= score <= 1.0
    assert score > 0  # Должен быть положительный score из-за общего тега 'python'


@pytest.mark.django_db
def test_recommendation_unique_constraint():
    teacher = User.objects.create_user(
        username='teacher17', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='student11', password='pass1234', role='student'
    )
    course = Course.objects.create(
        title='Test Course',
        owner=teacher,
        tags=['test'],
        difficulty='beginner'
    )
    
    # Создаем первую рекомендацию
    recommendation1 = Recommendation.objects.create(
        user=student,
        course=course,
        score=0.8,
        reason='Test reason'
    )
    
    # Проверяем, что создалась только одна рекомендация
    recommendations = Recommendation.objects.filter(user=student, course=course)
    assert recommendations.count() == 1
    assert recommendations.first().score == 0.8
    
    # Пытаемся создать дублирующую рекомендацию - должно вызвать исключение
    import pytest
    from django.db.utils import IntegrityError
    
    with pytest.raises(IntegrityError):
        Recommendation.objects.create(
            user=student,
            course=course,
            score=0.9,
            reason='Updated reason'
        )


@pytest.mark.django_db
def test_activity_unique_constraint():
    teacher = User.objects.create_user(
        username='teacher18', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='student12', password='pass1234', role='student'
    )
    course = Course.objects.create(
        title='Test Course',
        owner=teacher,
        tags=['test'],
        difficulty='beginner'
    )
    
    # Создаем активность
    activity1 = UserActivity.objects.create(
        user=student,
        course=course,
        activity_type='view'
    )
    
    # Создаем еще одну активность того же типа
    activity2 = UserActivity.objects.create(
        user=student,
        course=course,
        activity_type='view'
    )
    
    # Проверяем, что обе активности создались (unique constraint по created_at)
    activities = UserActivity.objects.filter(user=student, course=course, activity_type='view')
    assert activities.count() == 2
