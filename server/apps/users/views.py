from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from apps.common.permissions import AuthenticatedPermission

from .serializers import LoginSerializer, RegistrationSerializer, UserSerializer


class RegistrationView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token, _ = Token.objects.get_or_create(user=serializer.validated_data["user"])

        return Response(
            {
                "token": token.key,
                "user": UserSerializer(serializer.validated_data["user"]).data,
            }
        )


class MeView(APIView):
    permission_classes = (AuthenticatedPermission,)

    def get(self, request):
        return Response(UserSerializer(request.user).data)
