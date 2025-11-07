# Модель не обязательна для данного задания — файлы используются как основное хранилище.
from django.db import models

class Dummy(models.Model):
    created = models.DateTimeField(auto_now_add=True)
