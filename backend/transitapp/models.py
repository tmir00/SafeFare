from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, make_password, PermissionsMixin
from django.db import models
import hashlib


class CustomUserManager(BaseUserManager):
    def create_user(self, username, recovery_seed_hash, password=None):
        """
        Create and save a User with the given username and password.
        """
        if not username:
            raise ValueError('The Username must be set')
        user = self.model(username=username, recovery_seed_hash=recovery_seed_hash)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Create and save a SuperUser with the given username and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True, primary_key=True)
    number_of_tickets = models.IntegerField(default=0)
    recovery_seed_hash = models.CharField(max_length=255, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    tickets = models.ManyToManyField(Ticket, blank=True)  # Link to the Ticket model

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


    def reset_password_with_recovery_seed(self, recovery_seed, new_password):
        hashed_seed = hashlib.sha256(recovery_seed.encode()).hexdigest()

        if self.recovery_seed_hash == hashed_seed:
            self.password = make_password(new_password)
            self.save()
            return True
        else:
            return False


class Ticket(models.Model):
    ticket_id = models.CharField(max_length=100, unique=True)
    count = models.IntegerField
    charge = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.ticket_id

