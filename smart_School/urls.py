from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static

from home import  urls
from app_resources.urls import *
from livefeed import urls as livefeed_urls
from reports import urls as reporst_urls
from  authentications import  urls as auth_urls
from dashboard import urls as dashboard_urls
from config import urls as config_urls
from vehicle import urls as vehicle_urls
from smart_School import settings

urlpatterns = [
    path('',include(urls)),
    path('cameras/',include(url_cameras)),
    path('persons/',include(url_persons)),
    path('admin/',admin.site.urls),
    path('livefeed/',include(livefeed_urls)),
    path('reports/',include(reporst_urls)),
    path('accounts/',include(auth_urls)),
    path('dashboard/',include(dashboard_urls)),
    path('config/',include(config_urls)),
    path('vehicle/',include(vehicle_urls))

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
