from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .permissions import IsAdmin
from .serializers import UserSerializer
from .tasks import send_confirmation_email

# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class RegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_confirmation_email.delay(
                user.email, str(user.email_confirmation_token)
            )
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, token):
        user = get_object_or_404(User, email_confirmation_token=token)
        user.email_confirmed = True
        user.save(update_fields=['email_confirmed'])
        return Response({'detail': 'Email подтвержден!'}, status=status.HTTP_200_OK)
