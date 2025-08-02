from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
import urllib.request
import urllib.parse
import json


def build_confirmation_link(token: str) -> str:
    return f"http://localhost:8000/api/confirm-email/{token}/"


@shared_task
def send_confirmation_email(email: str, token: str):
    link = build_confirmation_link(token)
    send_mail(
        subject='Подтверждение email на Study Platform',
        message=f'Пожалуйста, подтвердите ваш email: {link}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


@shared_task
def send_telegram_notification(telegram_id: str, message: str):
    """Отправка уведомления в Telegram"""
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not bot_token:
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        'chat_id': telegram_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        # Используем urllib вместо requests
        data_bytes = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(url, data=data_bytes)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.getcode() == 200
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")
        return False


@shared_task
def send_course_notification(user_id: int, course_title: str, message: str):
    """Отправка уведомления о курсе"""
    from users.models import User
    
    try:
        user = User.objects.get(id=user_id)
        if user.telegram_id:
            telegram_message = f"📚 <b>Новый курс: {course_title}</b>\n\n{message}"
            send_telegram_notification.delay(user.telegram_id, telegram_message)
    except User.DoesNotExist:
        pass


@shared_task
def send_test_notification(user_id: int, test_title: str, score: float):
    """Отправка уведомления о результатах теста"""
    from users.models import User
    
    try:
        user = User.objects.get(id=user_id)
        if user.telegram_id:
            telegram_message = f"🧪 <b>Результаты теста: {test_title}</b>\n\nВаш результат: {score:.1%}"
            send_telegram_notification.delay(user.telegram_id, telegram_message)
    except User.DoesNotExist:
        pass
