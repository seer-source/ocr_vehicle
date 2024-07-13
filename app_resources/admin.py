from django.contrib import admin

from .models import Cameras, Persons, PersonsDetect,ImagesPerson,Vehicle

admin.site.register(Cameras)
admin.site.register(Persons)
admin.site.register(PersonsDetect)
admin.site.register(ImagesPerson)
admin.site.register(Vehicle)
