from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from api.views import *
router = DefaultRouter()
router.register(r'images', ImageViewSet, basename='image')

urlpatterns = [
    path('images/', include(router.urls)), 
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
   path('register/', UserRegister.as_view(), name='register'),
	#path('login', UserLogin.as_view(), name='login'),
	path('logout/', UserLogout.as_view(), name='logout'),
	path('user/', UserView.as_view(), name='user'),
   path('hello/', hello_view, name='hello_view'),
   
]
