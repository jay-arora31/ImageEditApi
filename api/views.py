from rest_framework import viewsets, status
from rest_framework.response import Response
from django.conf import settings
from PIL import Image as PilImage
from io import BytesIO
import boto3
from rest_framework.permissions import IsAuthenticated
from rest_framework import  permissions
from rest_framework.response import Response
from .models import Image
from rest_framework import  status
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.conf import settings
from io import BytesIO
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
import boto3
from rest_framework.exceptions import ValidationError
from PIL import Image as PilImage
from .models import Image
from .serializers import ImageSerializer
from api.models import AppUser 
import openai  
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import  login, logout
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from rest_framework import permissions, status
from .validations import custom_validation, validate_email, validate_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AppUser
from botocore.exceptions import ClientError
from openai.error import OpenAIError

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hello_view(request):
    return Response({"message": "Hello"})

class UserRegister(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            clean_data = custom_validation(request.data)
            serializer = UserRegisterSerializer(data=clean_data)
            if serializer.is_valid(raise_exception=True):
                user = serializer.create(clean_data)
                if user:
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserLogin(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request):
        try:
            data = request.data
            assert validate_email(data)
            assert validate_password(data)
            serializer = UserLoginSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                user = serializer.check_user(data)
                if user:
                    login(request, user)
                    return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserLogout(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)

class UserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)
    
class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        try:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)

            uploaded_image = request.FILES.get('image')
            prompt = request.data.get('prompt', '')

            s3_url = None
            dalle_image_url = None

            if uploaded_image:
                img = PilImage.open(uploaded_image)
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)
                s3_buffer = buffer.getvalue()

                s3 = boto3.client('s3')
                s3_key = f'images/{request.user.id}/{uploaded_image.name}'
                try:
                    s3.upload_fileobj(BytesIO(s3_buffer), settings.AWS_STORAGE_BUCKET_NAME, s3_key, ExtraArgs={'ContentType': 'image/png'})
                except ClientError as e:
                    return Response({"error": "Error uploading image to S3: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                s3_url = f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{s3_key}'

            self.perform_update(serializer)

            if s3_url:
                instance.s3_image_url = s3_url
            if prompt:
                instance.prompt = prompt

            instance.save()

            if prompt and uploaded_image:
                openai.api_key = settings.OPENAI_API_KEY
                buffer.seek(0)
                try:
                    response = openai.Image.create_edit(
                        image=buffer,
                        prompt=prompt,
                        n=1,
                        size="1024x1024"
                    )
                    dalle_image_url = response['data'][0]['url']
                except OpenAIError as e:
                    return Response({"error": "Error generating image with DALL·E: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                "original_image_url": s3_url,
                "dalle_edited_image_url": dalle_image_url,
                "image_data": serializer.data,
                "prompt": prompt
            }, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"error": "Invalid data provided: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An unexpected error occurred: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": "An error occurred while deleting the image: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            uploaded_image = request.FILES.get('image')
            prompt = request.data.get('prompt', 'Generate an image based on this uploaded image')
            if not uploaded_image:
                return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)

            img = PilImage.open(uploaded_image)
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            s3_buffer = buffer.getvalue()

            s3 = boto3.client('s3')
            s3_key = f'images/{request.user.id}/{uploaded_image.name}'
            try:
                s3.upload_fileobj(BytesIO(s3_buffer), settings.AWS_STORAGE_BUCKET_NAME, s3_key, ExtraArgs={'ContentType': 'image/png'})
            except ClientError as e:
                return Response({"error": "Error uploading image to S3: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            s3_url = f'https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{s3_key}'

            openai.api_key = settings.OPENAI_API_KEY
            buffer.seek(0)
            try:
                response = openai.Image.create_edit(
                    image=buffer,
                    prompt=prompt,
                    n=1,
                    size="1024x1024"
                )
                dalle_image_url = response['data'][0]['url']
            except OpenAIError as e:
                return Response({"error": "Error generating image with DALL·E: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            image_instance = Image.objects.create(
                user=AppUser.objects.get(username=request.user.username),
                s3_image_url=s3_url,
                prompt=prompt,
            )

            serializer = self.get_serializer(image_instance)
            return Response({
                "original_image_url": s3_url,
                "dalle_edited_image_url": dalle_image_url,
                "image_data": serializer.data,
                "prompt": prompt
            }, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"error": "Invalid data provided: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An unexpected error occurred: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)