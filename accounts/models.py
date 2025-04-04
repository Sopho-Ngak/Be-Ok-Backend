# Python imports
import uuid
from datetime import datetime, timedelta

# Django imports
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.utils import timezone
from PIL import Image


def upload_path(instance, filename):
    return '/'.join(['profile_pictures', str(instance.user.username), filename])

class UserManager(BaseUserManager):
    def create_user(self, email, username, full_name, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError(_("Users must have an email address"))
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            full_name=full_name,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    
    def create_superuser(
        self, email, username, full_name, password=None, **extra_fields
    ):
        """
        Creates and saves a admin with the given email and password.
        """
        user = self.create_user(
            email,
            username,
            full_name,
            password=password,
            **extra_fields,
        )
        user.is_active = True
        user.staff = True
        user.admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
    def search_user(self, name):
        return self.filter(Q(username__icontains=name) | Q(full_name__icontains=name))

class User(AbstractBaseUser, PermissionsMixin):
    # USER TYPE
    DOCTOR = 'doctor'
    PATIENT = 'patient'
    ADMIN = 'admin'

    # GENDER
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'

    # MARITAL STATUS
    SINGLE = 'single'
    MARRIED = 'married'
    DIVORCED = 'divorced'
    WIDOWED = 'widowed'
    NOT_SPECIFIED = 'unspecified'

    
    USER_TYPE_CHOICES = (
        (DOCTOR, 'Doctor'),
        (PATIENT, 'Patient'),
        (ADMIN, 'Admin'),
    )

    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other'),
    )

    MARITAL_STATUS_CHOICES = (
        (NOT_SPECIFIED, 'Not Specified'),
        (SINGLE, 'Single'),
        (MARRIED, 'Married'),
        (DIVORCED, 'Divorced'),
        (WIDOWED, 'Widowed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255, unique=True, blank=True, null=True)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=8, choices=GENDER_CHOICES, default=OTHER)
    marital_status = models.CharField(max_length=50, choices=MARITAL_STATUS_CHOICES, default=NOT_SPECIFIED)
    date_of_birth = models.DateField(blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default=PATIENT)
    about_me = models.TextField(blank=True, null=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ['email', 'full_name']

    objects = UserManager()

    def __str__(self):
        return str(self.username)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True
    
    def get_full_name(self) -> str:
        return self.full_name

    def get_short_name(self) -> str:
        return self.username

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        # Simplest possible answer: All admins
        return self.admin
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']


class VerificationCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=4, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
    @property
    def is_expired(self):
        return self.created_at + timezone.timedelta(minutes=30) < timezone.now()

class ProfilePicture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_picture')
    image = models.ImageField(upload_to=upload_path, default='default/default_profile_picture.png')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
    # def save(self, *args, **kwargs):
    #     # resize image
    #     super().save(*args, **kwargs)
    #     img = Image.open(self.image.path)
    #     if img.height > 300 or img.width > 300:
    #         output_size = (300, 300)
    #         img.thumbnail(output_size)
    #         img.save(self.image.path)
