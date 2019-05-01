from django.shortcuts import render
from django.http import HttpResponse
from django.views import View

from django.views.decorators.csrf import csrf_exempt
from .ddash import dispatcher, microbio_app1, microbio_app2, microbio_app3, app_test, microbio_app4, home
from . import models

# Create your views here.

# def home(request):
#     return HttpResponse(render(request, 'display/app_template.html', locals()))

### dash

class dash_app(View):

    app_name = 'app_test'

    def get(self, request):
        request.session['microbio_app_name'] = self.app_name
        if self.app_name == 'app_test':
            app = app_test()
        elif self.app_name == 'microbio_app1':
            app = microbio_app1()
        elif self.app_name == 'microbio_app2':
            app = microbio_app2()
        elif self.app_name == 'microbio_app3':
            app = microbio_app3()
        elif self.app_name == 'microbio_app4':
            all_pid = models.patient_data.objects.all().values_list('PatientID',flat=True)
            app = microbio_app4(all_pid)
        else:
            app = home()
        return HttpResponse(dispatcher(request,app))
    # def get(self, request, *args, **kwargs):
    #     return HttpResponse(dispatcher(request,eval(self.app_name)))


@csrf_exempt
def dash_ajax(request):
    app_name = request.session['microbio_app_name']
    if app_name == 'app_test':
        app = app_test()
    elif app_name == 'microbio_app1':
        app = microbio_app1()
    elif app_name == 'microbio_app2':
        app = microbio_app2()
    elif app_name == 'microbio_app3':
        app = microbio_app3()
    elif app_name == 'microbio_app4':
        all_pid = models.patient_data.objects.all().values_list('PatientID',flat=True)
        app = microbio_app4(all_pid)
    else:
        app = home()

    return HttpResponse(dispatcher(request,app), content_type='application/json')

