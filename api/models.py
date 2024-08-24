from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings

class AppUserManager(BaseUserManager):
    def create_user(self, email, username=None, password=None):
        if not email:
            raise ValueError('An email is required.')
        if not password:
            raise ValueError('A password is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(email, username, password)
        user.is_superuser = True
        user.is_staff = True  # Ensure superuser is also staff
        user.save(using=self._db)
        return user
    

class AppUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=50, unique=True)
    username = models.CharField(max_length=50)
    is_staff = models.BooleanField(default=False)  # Add is_staff field
    is_active = models.BooleanField(default=True)  # Add is_active field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    objects = AppUserManager()

    def __str__(self):
        return self.username

# Model to store metadata about images
class Image(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    s3_image_url = models.URLField(max_length=200)  
    uploaded_at = models.DateTimeField(auto_now_add=True)  
    edited_at = models.DateTimeField(auto_now=True) 
    prompt = models.TextField()  

    def __str__(self):
        return f"Image {self.id} by {self.user.username}"
    
class APIMetrics(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    endpoint = models.CharField(max_length=255)
    request_count = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"API Metrics for {self.user.username} on {self.endpoint}"
    
class FunctionMetrics(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    function_name = models.CharField(max_length=255)
    invocation_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Function {self.function_name} used by {self.user.username}"
    
class AggregateMetrics(models.Model):
    total_api_calls = models.PositiveIntegerField(default=0)
    total_function_usage = models.PositiveIntegerField(default=0)
    unique_user_count = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Aggregate Metrics as of {self.last_updated}"