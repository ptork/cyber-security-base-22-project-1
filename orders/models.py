from django.contrib.auth.models import User
from django.db import models

class Order(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  product = models.CharField(max_length=100)
  price = models.FloatField()
  status = models.CharField(max_length=100)
