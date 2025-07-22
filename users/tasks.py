from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


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
