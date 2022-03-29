from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  addressLine1 = models.CharField(max_length=100)
  addressLine2 = models.CharField(max_length=100)
  addressLine3 = models.CharField(max_length=100)
