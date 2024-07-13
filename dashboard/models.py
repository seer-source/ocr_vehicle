from django.db import models

from authentications.models import User

class NationaId(models.Model):
    frontImage=models.ImageField(upload_to='national_id/')
    image=models.ImageField(upload_to='national_id/')
    backImage=models.ImageField(upload_to='national_id/')

class Department(models.Model):
    name = models.CharField(max_length=500)
    user_manager=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    def __str__(self) -> str:
        return self.name
class Type(models.Model):
    type = models.CharField(max_length=500)
    def __str__(self) -> str:
        return self.type
class VisiTortype(models.Model):
    visitor_type = models.CharField(max_length=500) 
    def __str__(self) -> str:
        return self.visitor_type
class Reason(models.Model):
    reason = models.CharField(max_length=500)
    def __str__(self) -> str:
        return self.reason
class Other(models.Model):
    other = models.CharField(max_length=500) 
    def __str__(self) -> str:
        return self.other
