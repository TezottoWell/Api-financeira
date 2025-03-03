from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import RegistroSerializer, UsuarioSerializer


class RegistroView(generics.CreateAPIView):
    """
    View para registrar um novo usuário
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegistroSerializer


class UsuarioView(generics.RetrieveAPIView):
    """
    View para obter os detalhes do usuário autenticado
    """
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    """
    View para deslogar o usuário (invalidar o token)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
