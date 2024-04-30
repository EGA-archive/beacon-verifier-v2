from django.db import models

class TimeOfCollection(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class AgeOfOnset(models.Model):
    P67Y = models.BooleanField(max_length=200, unique=True)
    P65Y = models.BooleanField(max_length=200, unique=True)

    def __str__(self):
        return self.name