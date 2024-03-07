from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class MapGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)

    def __str__(self):
        return self.name
    
class Map(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    updated_at = models.DateTimeField(auto_now=True)
    #updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_by = models.CharField(max_length=100)
    map_group = models.ForeignKey(MapGroup, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name
    
class Hero(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    lvl = models.IntegerField()
    maps = models.ManyToManyField(Map)

    def __str__(self):
        return self.name

class Clan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    members = models.ManyToManyField(User, blank=True)
    admins = models.ManyToManyField(User, related_name = "clan_admin_set", blank=True)

    def __str__(self):
        return self.name