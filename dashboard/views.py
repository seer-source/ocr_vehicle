import base64
import json
from django.core.files.base import ContentFile
from django.shortcuts import redirect, render
from django.views import View
import requests
from config.models import Config
from dashboard.form import SearchIDForm
from app_resources.models import Cameras, Persons
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils.decorators import method_decorator
from livefeed.utils import search_by_image_person

@method_decorator(login_required, name='dispatch')
class SearchIDView(View):
    template_name='dashboard/search_id.html'
    form_class=SearchIDForm
    cameras=Cameras.objects.all()
    api_url = 'Config.objects.all().first().url_extract_data'
    def get(self,request):
        form=self.form_class()
        return render(request, 'dashboard/search_id.html', context={'form': form, "cameras":self.cameras})
    def post(self,request):
        form=self.form_class(request.POST, request.FILES)
        if form.is_valid():
            image=request.POST.get('frontImage')
            id=form.cleaned_data['National_id']
            person=self.__search_by_image_or_field(image,id)
            result=self.render_html(request,person)
            return result
        else:
            return render(request, self.template_name, context={'form': form, "cameras":self.cameras})
    
    def render_html(self,request,person):
        if person:
            return redirect('/persons/view_person/'+str(person.first().id))
        else:
            messages.error(request, ' الشخص غير موجود ')
            return render(request, self.template_name, context={'form': self.form_class(), "cameras":self.cameras})
            
    def __search_by_image_or_field(self,image,id):
        if  image:
            person=self.__search_by_image(image)
        else:
            person=self.__search_by_id_text(id)
        return person               
        
    def __search_by_id_text(self,id):
        person=Persons.objects.filter(id_national=id)
        return person
    def __search_by_image(self,image):
        file=self.__convert_image_to_file_to_send(image)
        response = requests.post(self.api_url, files=file)
        response_json = json.loads(response.text)
        person = Persons.objects.filter(id_national=response_json.get('iden').replace(' ', '')) 
        return person
    
    def __convert_image_to_file_to_send(self,image):
        data = json.loads(image)
        picture = ContentFile(base64.b64decode(data['data']),name=data['name'])
        file = {'file': ('filename.jpg', picture, 'image/jpeg')}
        return file
 
@method_decorator(login_required, name='dispatch')   
class FaceIdView(View):
    template_name='dashboard/face_id.html'
    form_class=SearchIDForm
    cameras=Cameras.objects.all()
    def get(self,request):
        return render(request,self.template_name, context={'form': self.form_class(), "cameras":self.cameras})
    def post(self,request):
        form=self.form_class(request.POST, request.FILES)
        if form.is_valid():
            image=request.POST.get('frontImage')
            data_image=self.__get_image(image)
            self.__search_person(data_image)
        else:
          return render(request,self.template_name, context={'form': form, "cameras":self.cameras}) 
           
    def __search_person(self,frame):
        if frame is not None:
           id=search_by_image_person(frame)
           if id:
              return redirect('person')
        return redirect('')
    def __get_image(self,image):
        if image: 
                data = json.loads(image)
                data_image = ContentFile(base64.b64decode(data['data']),name=data['name'])
                return data_image
        else:
            return None