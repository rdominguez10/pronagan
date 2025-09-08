from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# Create your models here.

class Admin_app(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields ):
        if not username:
            raise ValueError('El correo es obligatorio')
        #email = self.normalize_email(email)
        user = self.model(username=username,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class Usuario(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    last_login = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    intentos = models.IntegerField(default=1)
    

    objects = Admin_app()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    class Meta:
        db_table = 'admin_app' 
        managed = False