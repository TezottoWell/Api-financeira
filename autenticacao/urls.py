from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegistroView, UsuarioView, LogoutView

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('registro/', RegistroView.as_view(), name='registro'),
    path('usuario/', UsuarioView.as_view(), name='usuario'),
    path('logout/', LogoutView.as_view(), name='logout'),
] 