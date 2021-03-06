from django.conf.urls import url
from django.contrib.auth.views import logout

from . import views

urlpatterns = [
    url(r'^$', views.newAssesment3, name='newAssesment3'),
    url(r'^updategrade/$', views.updateGrade, name='updateGrade'),
    url(r'^obtenerassesment/$', views.getAssesment, name='getAssesment'),
    url(r'^obtenerassesment1/$', views.getStudentAssesment, name='getStudentAssesment'),
    url(r'^(?P<id_class>[0-9]+)/habilidades/$', 'bakhanapp.views.getSkillAssesment', name='getSkillAssesment'), 
    url(r'^updateassesment/$', views.updateAssesment, name='updateAssesment'),
    url(r'^gradeData/$', views.gradeData, name='gradeData'),
]