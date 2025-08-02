from django.db.models import Q, Avg, Count
from courses.models import Course, UserActivity, Recommendation
from users.models import User


class RecommendationService:
    """Сервис для генерации рекомендаций курсов"""
    
    @staticmethod
    def get_user_preferences(user):
        """Анализ предпочтений пользователя на основе активности"""
        activities = UserActivity.objects.filter(user=user).select_related('course')
        
        # Анализ по тегам
        tag_preferences = {}
        difficulty_preferences = {}
        
        for activity in activities:
            # Анализ тегов
            for tag in activity.course.tags:
                if tag in tag_preferences:
                    tag_preferences[tag] += 1
                else:
                    tag_preferences[tag] = 1
            
            # Анализ сложности
            difficulty = activity.course.difficulty
            if difficulty in difficulty_preferences:
                difficulty_preferences[difficulty] += 1
            else:
                difficulty_preferences[difficulty] = 1
        
        return {
            'tags': tag_preferences,
            'difficulty': difficulty_preferences,
            'avg_score': activities.aggregate(Avg('score'))['score__avg'] or 0
        }
    
    @staticmethod
    def calculate_course_score(user, course):
        """Расчет релевантности курса для пользователя"""
        preferences = RecommendationService.get_user_preferences(user)
        
        score = 0.0
        
        # Оценка по тегам
        for tag in course.tags:
            if tag in preferences['tags']:
                score += preferences['tags'][tag] * 0.3
        
        # Оценка по сложности
        if course.difficulty in preferences['difficulty']:
            score += preferences['difficulty'][course.difficulty] * 0.2
        
        # Оценка по популярности курса
        course_popularity = UserActivity.objects.filter(course=course).count()
        score += min(course_popularity * 0.01, 0.3)
        
        # Оценка по рейтингу курса
        avg_score = UserActivity.objects.filter(course=course).aggregate(Avg('score'))['score__avg']
        if avg_score:
            score += avg_score * 0.2
        
        return min(score, 1.0)
    
    @staticmethod
    def generate_recommendations(user, limit=5):
        """Генерация рекомендаций для пользователя"""
        # Получаем курсы, которые пользователь еще не проходил
        user_courses = UserActivity.objects.filter(user=user).values_list('course_id', flat=True)
        available_courses = Course.objects.exclude(id__in=user_courses)
        
        recommendations = []
        
        for course in available_courses:
            score = RecommendationService.calculate_course_score(user, course)
            
            if score > 0.1:  # Минимальный порог релевантности
                reason = RecommendationService._generate_reason(user, course, score)
                
                # Сохраняем или обновляем рекомендацию
                recommendation, created = Recommendation.objects.update_or_create(
                    user=user,
                    course=course,
                    defaults={
                        'score': score,
                        'reason': reason
                    }
                )
                
                recommendations.append(recommendation)
        
        # Сортируем по релевантности и возвращаем топ рекомендации
        return sorted(recommendations, key=lambda x: x.score, reverse=True)[:limit]
    
    @staticmethod
    def _generate_reason(user, course, score):
        """Генерация причины рекомендации"""
        preferences = RecommendationService.get_user_preferences(user)
        
        reasons = []
        
        # Причина по тегам
        common_tags = set(course.tags) & set(preferences['tags'].keys())
        if common_tags:
            reasons.append(f"Курс содержит интересующие вас теги: {', '.join(common_tags)}")
        
        # Причина по сложности
        if course.difficulty in preferences['difficulty']:
            reasons.append(f"Сложность курса соответствует вашему уровню")
        
        # Причина по популярности
        popularity = UserActivity.objects.filter(course=course).count()
        if popularity > 10:
            reasons.append("Популярный курс среди студентов")
        
        return "; ".join(reasons) if reasons else "Рекомендуется на основе вашей активности"


class ActivityService:
    """Сервис для отслеживания активности пользователей"""
    
    @staticmethod
    def track_activity(user, course, activity_type, score=None):
        """Отслеживание активности пользователя"""
        UserActivity.objects.create(
            user=user,
            course=course,
            activity_type=activity_type,
            score=score
        )
        
        # Генерируем новые рекомендации после активности
        RecommendationService.generate_recommendations(user)
    
    @staticmethod
    def get_user_progress(user):
        """Получение прогресса пользователя"""
        activities = UserActivity.objects.filter(user=user).select_related('course')
        
        progress = {
            'courses_viewed': activities.filter(activity_type='view').count(),
            'courses_completed': activities.filter(activity_type='complete').count(),
            'tests_passed': activities.filter(activity_type='test_passed').count(),
            'avg_score': activities.aggregate(Avg('score'))['score__avg'] or 0,
            'total_activities': activities.count()
        }
        
        return progress 