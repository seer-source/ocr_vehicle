from django.db import models
from datetime import time,datetime

from app_resources.models import Persons
from authentications.models import User
from django.utils import timezone

class Config(models.Model):
    time_start_working=models.TimeField(default=time(8, 0),null=True)
    num_end_permission=models.DecimalField(max_digits=10,decimal_places=2,default=8,null=True)
    num_hour_working=models.DecimalField(max_digits=10,decimal_places=2,default=2,null=True)
    url_extract_data=models.URLField(default='http://24.144.84.0:9090/api/',null=True)
    url_image=models.URLField(default='http://24.144.84.0:9090/api/',null=True)
    url_extract_data_back=models.URLField(default='http://24.144.84.0:9090/api_back/',null=True)
    token_access=models.CharField(max_length=500,null=True)
    url_whatsapp=models.URLField(default='https://graph.facebook.com/v17.0/119791417748534/messages',null=True)
    @property
    def time_end_working(self):
        start_time = self.time_start_working
        num_hours = self.num_hour_working
        hours, minutes = divmod(int(num_hours * 60), 60)
        hours = hours % 24

        end_time = time((start_time.hour + hours) % 24, start_time.minute + minutes)
        return end_time
    def save(self, *args, **kwargs):
        if self.time_start_working is None:
            self.time_start_working = time(8, 0)
        if self.num_end_permission is None:
            self.num_end_permission = 8
        if self.num_hour_working is None:
            self.num_hour_working = 2
        if self.url_extract_data is None:
            self.url_extract_data = 'http://24.144.84.0:9090/api/'
        if self.url_image is None:
            self.url_image = 'http://24.144.84.0:9090/api/'
        if self.url_extract_data_back is None:
            self.url_extract_data_back = 'http://24.144.84.0:9090/api_back/'
        if self.url_whatsapp is None:
            self.url_whatsapp = 'https://graph.facebook.com/v17.0/119791417748534/messages'
            
        super().save(*args, **kwargs)
    

class AddDuration(models.Model):
    name=models.CharField(max_length=100)
    num_hour_working=models.DecimalField(max_digits=10,decimal_places=2,default=8)
    persions=models.ManyToManyField(Persons,blank=True)
class Nabatshieh(models.Model):
    name=models.CharField(max_length=100)
    time_start_working=models.TimeField(default=time(8, 0))
    num_hour_working=models.DecimalField(max_digits=10,decimal_places=2,default=8)
    persions=models.ManyToManyField(Persons,blank=True)
    @property
    def time_end_working(self):
        start_time = self.time_start_working
        num_hours = self.num_hour_working
        hours, minutes = divmod(int(num_hours * 60), 60)
        hours = hours % 24
        end_time = time((start_time.hour + hours) % 24, start_time.minute + minutes)
        return end_time
    

when_chooses = [
        ('الدخول', 'الدخول'),
        ('الخروج', 'الخروج')
    ]
class Reasons(models.Model):
    name=models.CharField(max_length=200)
    fromm=models.TimeField(null=True,blank=True)
    too=models.TimeField(null=True,blank=True)
    persions=models.ManyToManyField(Persons,blank=True)
    num_reason=models.IntegerField()
    when=models.CharField(
        max_length=20,
        choices=when_chooses,
        default='entry'
    )
    def __str__(self):
        return f'{self.name}---{self.when}'

    

class Permission(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    time_exc_permission = models.DurationField(null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by_permissions',null=True)
    reason = models.ForeignKey(Reasons, on_delete=models.CASCADE)
    is_accept=models.BooleanField(null=True)
    for_emp = models.ManyToManyField(Persons,blank=True)
    
    def change_status(self,value):
        self.is_accept=value
        self.save()
   
    def execute(self):
        end_time = timezone.now()
        start_time = self.created_at
        time_diff = end_time - start_time
        self.time_exc_permission = time_diff
        self.save()
