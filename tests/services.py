from .models import Answer, Test, TestResult


def check_test_answers(test: Test, user, answers_data: dict) -> TestResult:
    """
    answers_data: {question_id: answer_id, ...}
    """
    questions = test.questions.all()
    total = questions.count()
    correct = 0
    for question in questions:
        answer_id = answers_data.get(str(question.id))
        if answer_id:
            try:
                answer = Answer.objects.get(id=answer_id, question=question)
                if answer.is_correct:
                    correct += 1
            except Answer.DoesNotExist:
                pass
    score = correct / total if total > 0 else 0
    result = TestResult.objects.create(test=test, user=user, score=score)
    return result
