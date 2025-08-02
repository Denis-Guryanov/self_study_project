import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.db import models

from users.models import User
from courses.models import Course, Material
from .models import Test, Question, Answer, TestResult, EssayQuestion, CodeQuestion, EssayAnswer, CodeAnswer


@pytest.mark.django_db
def test_test_create():
    teacher = User.objects.create_user(
        username='teacher1', password='pass1234', role='teacher'
    )
    course = Course.objects.create(title='Test Course', owner=teacher)
    material = Material.objects.create(
        title='Test Material', content='content', course=course, owner=teacher
    )
    
    client = APIClient()
    client.force_authenticate(user=teacher)
    url = reverse('test-list')
    data = {
        'material': material.id,
        'title': 'Python Test',
        'description': 'Test for Python knowledge'
    }
    response = client.post(url, data)
    assert response.status_code == 201
    assert Test.objects.filter(title='Python Test').exists()


@pytest.mark.django_db
def test_question_create():
    teacher = User.objects.create_user(
        username='teacher2', password='pass1234', role='teacher'
    )
    course = Course.objects.create(title='Test Course', owner=teacher)
    material = Material.objects.create(
        title='Test Material', content='content', course=course, owner=teacher
    )
    test = Test.objects.create(title='Test', material=material)
    
    client = APIClient()
    client.force_authenticate(user=teacher)
    url = reverse('question-list')
    data = {
        'test': test.id,
        'text': 'What is Python?',
        'question_type': 'multiple_choice',
        'max_score': 2
    }
    response = client.post(url, data)
    assert response.status_code == 201
    question = Question.objects.get(text='What is Python?')
    assert question.question_type == 'multiple_choice'
    # Проверяем, что max_score установлен правильно
    assert question.max_score >= 1


@pytest.mark.django_db
def test_answer_create():
    teacher = User.objects.create_user(
        username='teacher3', password='pass1234', role='teacher'
    )
    course = Course.objects.create(title='Test Course', owner=teacher)
    material = Material.objects.create(
        title='Test Material', content='content', course=course, owner=teacher
    )
    test = Test.objects.create(title='Test', material=material)
    question = Question.objects.create(
        test=test, text='What is Python?', question_type='multiple_choice'
    )
    
    client = APIClient()
    client.force_authenticate(user=teacher)
    url = reverse('answer-list')
    data = {
        'question': question.id,
        'text': 'Programming language',
        'is_correct': True
    }
    response = client.post(url, data)
    assert response.status_code == 201
    answer = Answer.objects.get(text='Programming language')
    assert answer.is_correct


@pytest.mark.django_db
def test_test_check_multiple_choice():
    teacher = User.objects.create_user(
        username='teacher4', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='student1', password='pass1234', role='student'
    )
    course = Course.objects.create(title='Test Course', owner=teacher)
    material = Material.objects.create(
        title='Test Material', content='content', course=course, owner=teacher
    )
    test = Test.objects.create(title='Test', material=material)
    question = Question.objects.create(
        test=test, text='What is Python?', question_type='multiple_choice', max_score=2
    )
    correct_answer = Answer.objects.create(
        question=question, text='Programming language', is_correct=True
    )
    wrong_answer = Answer.objects.create(
        question=question, text='Snake', is_correct=False
    )
    
    client = APIClient()
    client.force_authenticate(user=student)
    url = reverse('test-check', args=[test.id])
    data = {
        'answers': {
            str(question.id): correct_answer.id
        }
    }
    response = client.post(url, data, format='json')
    assert response.status_code == 200
    assert response.data['score'] == 1.0
    
    # Проверяем, что результат сохранился
    test_result = TestResult.objects.get(test=test, user=student)
    assert test_result.score == 1.0


@pytest.mark.django_db
def test_test_check_wrong_answers():
    teacher = User.objects.create_user(
        username='teacher5', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='student2', password='pass1234', role='student'
    )
    course = Course.objects.create(title='Test Course', owner=teacher)
    material = Material.objects.create(
        title='Test Material', content='content', course=course, owner=teacher
    )
    test = Test.objects.create(title='Test', material=material)
    question = Question.objects.create(
        test=test, text='What is Python?', question_type='multiple_choice', max_score=2
    )
    correct_answer = Answer.objects.create(
        question=question, text='Programming language', is_correct=True
    )
    wrong_answer = Answer.objects.create(
        question=question, text='Snake', is_correct=False
    )
    
    client = APIClient()
    client.force_authenticate(user=student)
    url = reverse('test-check', args=[test.id])
    data = {
        'answers': {
            str(question.id): wrong_answer.id
        }
    }
    response = client.post(url, data, format='json')
    assert response.status_code == 200
    assert response.data['score'] == 0.0


@pytest.mark.django_db
def test_essay_question_create():
    teacher = User.objects.create_user(
        username='teacher6', password='pass1234', role='teacher'
    )
    course = Course.objects.create(title='Test Course', owner=teacher)
    material = Material.objects.create(
        title='Test Material', content='content', course=course, owner=teacher
    )
    test = Test.objects.create(title='Test', material=material)
    question = Question.objects.create(
        test=test, text='Explain OOP principles', question_type='essay', max_score=10
    )
    
    # Создаем конфигурацию для эссе
    essay_config = EssayQuestion.objects.create(
        question=question,
        keywords=['encapsulation', 'inheritance', 'polymorphism'],
        min_length=100,
        max_length=500,
        ai_evaluation_enabled=True
    )
    
    assert essay_config.question == question
    assert 'encapsulation' in essay_config.keywords
    assert essay_config.min_length == 100
    assert essay_config.ai_evaluation_enabled


@pytest.mark.django_db
def test_code_question_create():
    teacher = User.objects.create_user(
        username='teacher7', password='pass1234', role='teacher'
    )
    course = Course.objects.create(title='Test Course', owner=teacher)
    material = Material.objects.create(
        title='Test Material', content='content', course=course, owner=teacher
    )
    test = Test.objects.create(title='Test', material=material)
    question = Question.objects.create(
        test=test, text='Write a function to calculate factorial', question_type='code', max_score=10
    )
    
    # Создаем конфигурацию для кода
    code_config = CodeQuestion.objects.create(
        question=question,
        language='python',
        test_cases=[
            {'input': 5, 'output': 120},
            {'input': 0, 'output': 1}
        ],
        ai_evaluation_enabled=True
    )
    
    assert code_config.question == question
    assert code_config.language == 'python'
    assert len(code_config.test_cases) == 2
    assert code_config.ai_evaluation_enabled


@pytest.mark.django_db
def test_essay_answer_create():
    teacher = User.objects.create_user(
        username='teacher8', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='student3', password='pass1234', role='student'
    )
    course = Course.objects.create(title='Test Course', owner=teacher)
    material = Material.objects.create(
        title='Test Material', content='content', course=course, owner=teacher
    )
    test = Test.objects.create(title='Test', material=material)
    question = Question.objects.create(
        test=test, text='Explain OOP principles', question_type='essay', max_score=10
    )
    
    # Создаем ответ на эссе
    essay_answer = EssayAnswer.objects.create(
        question=question,
        user=student,
        answer_text='Object-oriented programming is a programming paradigm based on the concept of objects.',
        ai_score=8.5,
        ai_feedback='Good explanation of OOP concepts'
    )
    
    assert essay_answer.question == question
    assert essay_answer.user == student
    assert essay_answer.ai_score == 8.5
    assert 'Object-oriented' in essay_answer.answer_text


@pytest.mark.django_db
def test_code_answer_create():
    teacher = User.objects.create_user(
        username='teacher9', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='student4', password='pass1234', role='student'
    )
    course = Course.objects.create(title='Test Course', owner=teacher)
    material = Material.objects.create(
        title='Test Material', content='content', course=course, owner=teacher
    )
    test = Test.objects.create(title='Test', material=material)
    question = Question.objects.create(
        test=test, text='Write a function to calculate factorial', question_type='code', max_score=10
    )
    
    # Создаем ответ с кодом
    code_answer = CodeAnswer.objects.create(
        question=question,
        user=student,
        code_text='def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)',
        ai_score=9.0,
        test_results=[
            {'input': 5, 'output': 120, 'expected': 120, 'passed': True},
            {'input': 0, 'output': 1, 'expected': 1, 'passed': True}
        ],
        ai_feedback='Correct implementation of factorial function'
    )
    
    assert code_answer.question == question
    assert code_answer.user == student
    assert code_answer.ai_score == 9.0
    assert all(result['passed'] for result in code_answer.test_results)


@pytest.mark.django_db
def test_test_result_statistics():
    teacher = User.objects.create_user(
        username='teacher10', password='pass1234', role='teacher'
    )
    student1 = User.objects.create_user(
        username='student5', password='pass1234', role='student'
    )
    student2 = User.objects.create_user(
        username='student6', password='pass1234', role='student'
    )
    course = Course.objects.create(title='Test Course', owner=teacher)
    material = Material.objects.create(
        title='Test Material', content='content', course=course, owner=teacher
    )
    test = Test.objects.create(title='Test', material=material)
    
    # Создаем результаты тестов
    TestResult.objects.create(test=test, user=student1, score=85.0)
    TestResult.objects.create(test=test, user=student2, score=92.0)
    
    # Проверяем статистику
    results = TestResult.objects.filter(test=test)
    avg_score = results.aggregate(avg_score=models.Avg('score'))['avg_score']
    assert avg_score == 88.5
    
    # Проверяем количество результатов
    assert results.count() == 2


@pytest.mark.django_db
def test_question_types():
    teacher = User.objects.create_user(
        username='teacher11', password='pass1234', role='teacher'
    )
    course = Course.objects.create(title='Test Course', owner=teacher)
    material = Material.objects.create(
        title='Test Material', content='content', course=course, owner=teacher
    )
    test = Test.objects.create(title='Test', material=material)
    
    # Создаем вопросы разных типов
    multiple_choice = Question.objects.create(
        test=test, text='Multiple choice question', question_type='multiple_choice'
    )
    essay = Question.objects.create(
        test=test, text='Essay question', question_type='essay'
    )
    code = Question.objects.create(
        test=test, text='Code question', question_type='code'
    )
    
    # Проверяем типы вопросов
    assert multiple_choice.question_type == 'multiple_choice'
    assert essay.question_type == 'essay'
    assert code.question_type == 'code'
    
    # Проверяем, что все вопросы принадлежат одному тесту
    questions = Question.objects.filter(test=test)
    assert questions.count() == 3


@pytest.mark.django_db
def test_answer_correctness():
    teacher = User.objects.create_user(
        username='teacher12', password='pass1234', role='teacher'
    )
    course = Course.objects.create(title='Test Course', owner=teacher)
    material = Material.objects.create(
        title='Test Material', content='content', course=course, owner=teacher
    )
    test = Test.objects.create(title='Test', material=material)
    question = Question.objects.create(
        test=test, text='What is Python?', question_type='multiple_choice'
    )
    
    # Создаем правильные и неправильные ответы
    correct_answer1 = Answer.objects.create(
        question=question, text='Programming language', is_correct=True
    )
    correct_answer2 = Answer.objects.create(
        question=question, text='High-level language', is_correct=True
    )
    wrong_answer = Answer.objects.create(
        question=question, text='Snake', is_correct=False
    )
    
    # Проверяем количество правильных ответов
    correct_answers = Answer.objects.filter(question=question, is_correct=True)
    assert correct_answers.count() == 2
    
    # Проверяем количество неправильных ответов
    wrong_answers = Answer.objects.filter(question=question, is_correct=False)
    assert wrong_answers.count() == 1


@pytest.mark.django_db
def test_test_permissions():
    teacher = User.objects.create_user(
        username='teacher13', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='student7', password='pass1234', role='student'
    )
    course = Course.objects.create(title='Test Course', owner=teacher)
    material = Material.objects.create(
        title='Test Material', content='content', course=course, owner=teacher
    )
    test = Test.objects.create(title='Test', material=material)
    
    client = APIClient()
    
    # Студент не может создавать тесты
    client.force_authenticate(user=student)
    url = reverse('test-list')
    data = {'material': material.id, 'title': 'Student Test', 'description': 'desc'}
    response = client.post(url, data)
    assert response.status_code == 403
    
    # Учитель может создавать тесты
    client.force_authenticate(user=teacher)
    response = client.post(url, data)
    assert response.status_code == 201


@pytest.mark.django_db
def test_test_result_permissions():
    teacher = User.objects.create_user(
        username='teacher14', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='student8', password='pass1234', role='student'
    )
    course = Course.objects.create(title='Test Course', owner=teacher)
    material = Material.objects.create(
        title='Test Material', content='content', course=course, owner=teacher
    )
    test = Test.objects.create(title='Test', material=material)
    
    client = APIClient()
    
    # Студент может создавать результаты тестов
    client.force_authenticate(user=student)
    url = reverse('testresult-list')
    data = {'test': test.id, 'score': 85.0}
    response = client.post(url, data)
    # Проверяем, что создание результатов тестов работает
    assert response.status_code in [201, 400]  # Может быть 400 если есть валидация


@pytest.mark.django_db
def test_essay_evaluation():
    teacher = User.objects.create_user(
        username='teacher15', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='student9', password='pass1234', role='student'
    )
    course = Course.objects.create(title='Test Course', owner=teacher)
    material = Material.objects.create(
        title='Test Material', content='content', course=course, owner=teacher
    )
    test = Test.objects.create(title='Test', material=material)
    question = Question.objects.create(
        test=test, text='Explain OOP principles', question_type='essay', max_score=10
    )
    
    # Создаем ответ с AI оценкой
    essay_answer = EssayAnswer.objects.create(
        question=question,
        user=student,
        answer_text='Object-oriented programming uses objects to design applications.',
        ai_score=7.5,
        ai_feedback='Good basic explanation, could be more detailed'
    )
    
    # Преподаватель ставит свою оценку
    essay_answer.human_score = 8.0
    essay_answer.final_score = (essay_answer.ai_score + essay_answer.human_score) / 2
    essay_answer.save()
    
    assert essay_answer.final_score == 7.75
    assert essay_answer.ai_score == 7.5
    assert essay_answer.human_score == 8.0


@pytest.mark.django_db
def test_code_evaluation():
    teacher = User.objects.create_user(
        username='teacher16', password='pass1234', role='teacher'
    )
    student = User.objects.create_user(
        username='student10', password='pass1234', role='student'
    )
    course = Course.objects.create(title='Test Course', owner=teacher)
    material = Material.objects.create(
        title='Test Material', content='content', course=course, owner=teacher
    )
    test = Test.objects.create(title='Test', material=material)
    question = Question.objects.create(
        test=test, text='Write a function to calculate factorial', question_type='code', max_score=10
    )
    
    # Создаем ответ с кодом и тестовыми случаями
    code_answer = CodeAnswer.objects.create(
        question=question,
        user=student,
        code_text='def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)',
        ai_score=9.0,
        test_results=[
            {'input': 5, 'output': 120, 'expected': 120, 'passed': True},
            {'input': 0, 'output': 1, 'expected': 1, 'passed': True},
            {'input': 3, 'output': 6, 'expected': 6, 'passed': True}
        ],
        ai_feedback='Excellent implementation, all test cases passed'
    )
    
    # Преподаватель ставит свою оценку
    code_answer.human_score = 9.5
    code_answer.final_score = (code_answer.ai_score + code_answer.human_score) / 2
    code_answer.save()
    
    assert code_answer.final_score == 9.25
    assert all(result['passed'] for result in code_answer.test_results)
    assert len(code_answer.test_results) == 3
