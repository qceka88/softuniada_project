import json

from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from simplejwt import jwt
from softuniada_project.settings import SECRET_KEY
from jwt.algorithms import get_default_algorithms
from jwt.api_jwt import PyJWT

from .serializer import BookModelSerializer, UserSerializer
from .models import Book, User


# Create your views here.


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookModelSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user_view(request):
    if request.method == 'POST':
        data = request.data.copy()
        emails = User.objects.values_list('email', flat=True)

        if data['email'] in emails:
            message = {'message': 'Email is already used'}
            return JsonResponse(message, status=status.HTTP_400_BAD_REQUEST)

        if 'password' in data:
            data['password'] = make_password(data['password'])

        serializer = UserSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    all_usernames = User.objects.values_list('email', flat=True)

    if email and password:
        if email in all_usernames:
            user = User.objects.get(email=email)
            if check_password(password, user.password):
                refresh_payload = {
                    'user_id': user.id,
                    'email': user.email,
                    'type': 'refresh',
                }

                key = SECRET_KEY

                refresh_token = PyJWT().encode(refresh_payload, key, algorithm='HS256')

                access_payload = {
                    'user_id': user.id,
                    'email': user.email,
                    'type': 'access',
                }

                access_token = PyJWT().encode(access_payload, key, algorithm='HS256')

                return Response({
                    'access_token': str(access_token),
                    'refresh_token': str(refresh_token),
                }, status=status.HTTP_200_OK)

    return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
