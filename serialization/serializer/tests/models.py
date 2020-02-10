from django.db import models


class BasicModel(models.Model):
    name = models.CharField(max_length=100)


# Relations


class ModelSimpleParent(models.Model):
    name = models.CharField(max_length=100)


class ModelChild(models.Model):
    name = models.CharField(max_length=100)
    related = models.ForeignKey(ModelSimpleParent, on_delete=models.CASCADE)
