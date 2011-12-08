from django.db import models


# Create your models here.
class FakeSouthModel(models.Model):
    name = models.CharField(max_length=128)
