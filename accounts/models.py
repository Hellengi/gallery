from django.db import models


class User(models.Model):
    name = models.CharField('Имя', max_length=120, unique=True)
    password = models.CharField('Пароль', max_length=120)

    def __str__(self):
        return f"{self.name}"
