import jwt

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db import models


class UserManager(BaseUserManager):

    # create user
    def create_user(self, username, email, password=None, **kwargs):
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save()

        return user

    # create super user with admin permissions
    def create_superuser(self, username, email, password):

        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=300, null=True)
    last_name = models.CharField(max_length=300, null=True)
    username = models.CharField(max_length=300, null=True, unique=True, db_index=True)
    email = models.EmailField(max_length=300, unique=True, null=True, db_index=True)
    password = models.CharField(max_length=1000, default='password')
    is_active = models.BooleanField(default=False)
    last_login_ip = models.CharField(max_length=300, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return str(self.username)

    @property
    def token(self):
        return str(self._generate_jwt_token())

    def get_full_name(self):
        return str(self.username)

    def get_short_name(self):
        return str(self.username)

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.pk,
            'exp': dt.utcfromtimestamp(dt.timestamp())
        }, settings.SECRET_KEY, algorithm='HS256')

        return str(token.decode('utf-8'))

    class Meta:
        db_table = 'approval_authentication_user'


class BlackListedToken(models.Model):
    token = models.CharField(max_length=600)
    user = models.ForeignKey(User, related_name="token_user", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("token", "user")

class Approval(models.Model):
    APPROVAL_CHOICES = (
        ("alpha", "Alpha"),
        ("beta", "Beta"),
        ("gamma", "Gamma"),
    )
    step = models.CharField(max_length=250, blank=True, null=True, choices=APPROVAL_CHOICES, default="alpha")
    users = models.ManyToManyField('User', related_name='users', null=True, blank=True)
    minimum_approver = models.IntegerField(blank=True, null=True)
    approval_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    approved = models.BooleanField(default=False)


class UserApproval(models.Model):
    approval = models.ForeignKey("Approval", on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=True, blank=True)
    approved = models.BooleanField(default=False)
    active = models.BooleanField(default=False)