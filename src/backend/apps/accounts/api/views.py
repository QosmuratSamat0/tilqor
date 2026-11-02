from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.serializers import (
    CurrentUserSerializer,
    LoginSerializer,
    RegisterSerializer,
)
from apps.accounts.services import register_user
from common.serializers import ErrorSerializer


@method_decorator(ensure_csrf_cookie, name="get")
class CsrfView(APIView):
    """Sets the CSRF cookie that the frontend sends back on state-changing requests."""

    permission_classes = [AllowAny]

    @extend_schema(tags=["auth"], responses={204: None})
    def get(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["auth"],
        request=RegisterSerializer,
        responses={201: CurrentUserSerializer, 400: ErrorSerializer},
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = register_user(**serializer.validated_data)
        login(request, user)
        return Response(CurrentUserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["auth"],
        request=LoginSerializer,
        responses={200: CurrentUserSerializer, 400: ErrorSerializer},
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, **serializer.validated_data)
        if user is None:
            return Response(
                {"detail": "Invalid username or password."}, status=status.HTTP_400_BAD_REQUEST
            )
        login(request, user)
        return Response(CurrentUserSerializer(user).data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["auth"],
        request=None,
        responses={204: None, 403: ErrorSerializer},
    )
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["auth"],
        responses={200: CurrentUserSerializer, 403: ErrorSerializer},
    )
    def get(self, request):
        return Response(CurrentUserSerializer(request.user).data)
