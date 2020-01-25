from django.db import models


# !! Need to rest migration if model field has changed
# Create your models here.
class Users(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    email = models.EmailField(max_length=128, unique=True)

    def __str__(self):
        return self.first_name + " " + self.last_name



