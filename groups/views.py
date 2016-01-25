# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-
from django.shortcuts import render,HttpResponseRedirect,render_to_response, redirect,HttpResponse
from django.template.context import RequestContext
from django.contrib.auth import  login,authenticate,logout
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
from django.db.models import Count

from django import template
from bakhanapp.models import Assesment_Skill
register = template.Library()

from bakhanapp.models import Class
from bakhanapp.models import Skill
from bakhanapp.models import Skill_Progress
from bakhanapp.models import Student
from bakhanapp.models import Student_Class
from bakhanapp.models import Student_Video
from bakhanapp.models import Student_Skill
from bakhanapp.models import Video_Playing
from bakhanapp.models import Skill_Attempt
from bakhanapp.models import Assesment_Skill
from bakhanapp.models import Class_Subject
from bakhanapp.models import Assesment
from bakhanapp.models import Assesment_Config
from bakhanapp.models import Subtopic_Skill
from bakhanapp.models import Subtopic_Video
from bakhanapp.models import Grade,Skill,Student_Skill,Skill_Progress
from bakhanapp.models import Subject,Chapter,Topic,Subtopic,Subtopic_Skill

import datetime

import cgi
import rauth
import SimpleHTTPServer
import SocketServer
import time
import webbrowser
import psycopg2

import json
import sys
from pprint import pprint
import codecs
from lib2to3.fixer_util import String
from django.core import serializers
from django.db import connection

from bakhanapp.models import Group,Group_Student
from django.utils import timezone
from bakhanapp.views import getTopictree


# Create your views here.
@login_required()
def getGroups(request, id_class):
    topictree=getTopictree('math') #Modificar para que busque el topic tree completo (desde su root)
    if request.method == 'POST':
        args = request.POST
        skills_selected = eval(args['skills'])
        if args["student_groups"]:#si se ha seleccionado la opcion guardar agrupacion.
            new_advanced = Group()
            new_advanced.name = 'test_advanced'
            new_advanced.type = 'advanced'
            new_advanced.start_date = timezone.now()
            new_advanced.end_date = timezone.now()
            new_advanced.kaid_student_tutor_id = 'kaid_1097501097555535353578558'
            new_advanced.save()
            new_intermediate = Group()
            new_intermediate.name = 'test_intermediate'
            new_intermediate.type = 'intermediate'
            new_intermediate.start_date = timezone.now()
            new_intermediate.end_date = timezone.now()
            new_intermediate.kaid_student_tutor_id = 'kaid_1097501097555535353578558'
            new_intermediate.save()
            new_reinforcement = Group()
            new_reinforcement.name = 'test_reinforcement'
            new_reinforcement.type = 'reinforcement'
            new_reinforcement.start_date = timezone.now()
            new_reinforcement.end_date = timezone.now()
            new_reinforcement.kaid_student_tutor_id = 'kaid_1097501097555535353578558'
            new_reinforcement.save()
            groups = eval(args['student_groups'])
            for g in groups:
                if g['group'] == 'Intermedios':
                    Group_Student(id_group_id=new_intermediate.id_group,
                                  kaid_student_id=g['kaid_student']).save()
                if g['group'] == 'Avanzados':
                    Group_Student(id_group_id=new_advanced.id_group,
                                  kaid_student_id=g['kaid_student']).save()
                if g['group'] == 'Reforzamiento':
                    Group_Student(id_group_id=new_reinforcement.id_group,
                                  kaid_student_id=g['kaid_student']).save()
            students = Student.objects.filter(kaid_student__in=Student_Class.objects.filter(id_class_id=id_class).values('kaid_student'))
            for s in students:
                s.type = 'ungrouped'
        students = makeGroups(id_class,skills_selected)
        return HttpResponse(students)
    else:
        students = Student.objects.filter(kaid_student__in=Student_Class.objects.filter(id_class_id=id_class).values('kaid_student'))
        for s in students:
            s.type = 'ungrouped'
    return render_to_response('groups.html',{'students': students,'topictree':topictree,'id_class':id_class},context_instance=RequestContext(request))

def makeGroups(id_class,skills_selected):
    #Funcion que entrega un arreglo con los estudiantes y su nivel de agrupamiento.
    #print skills_selected                                                         #aqui llegan bien las habilidades seleccionadas
    students = Student.objects.filter(kaid_student__in=Student_Class.objects.filter(id_class_id=id_class).values('kaid_student'))#retorna todos los estudiantes de un curso
    data = []  
    for s in students:
        #Por cada estudiante en id_class, se obtiene su agrupacion.
        s.type = getTypeStudent(s.kaid_student,skills_selected) #args debe contener todas las id de las skill seleccionadas para el agrupamiento.
        student={}
        student["kaid_student"] = s.kaid_student
        student["name"] = s.name
        student["type"] = s.type
        data.append(student)
        
    json_data = json.dumps(data)
    print json_data
    return json_data

def getTypeStudent(kaid_student,args):
    #Funcion que entrega en que nivel grupo debe ser organizado un estudiante
    #de acuerdo a su nivel en las skills seleccionadas por el profesor.
    #skills = Group_Skill.objects.filter(id_group_id=id_group)
    #aqui llegan bien las habilidades seleccionadas
    reinforcement = 0
    intermediate = 0
    advanced = 0
    total = len(args)
    for skill in args:
        student_progress = Student_Skill.objects.filter(kaid_student_id=kaid_student,id_skill_name_id=skill).values('last_skill_progress')
        #el problema esta con la variable student_progress
        if student_progress:
            if student_progress[0]["last_skill_progress"] == 'struggling' or student_progress[0]["last_skill_progress"] == 'unstarted':
                reinforcement += 1
            if student_progress[0]["last_skill_progress"] == 'mastery1' or student_progress[0]["last_skill_progress"] == 'mastery2' or student_progress[0]["last_skill_progress"] == 'practiced':
                intermediate += 1
            if student_progress[0]["last_skill_progress"] == 'mastery3':
                advanced += 1
    if reinforcement > 0:
        return 'reinforcement'
    elif intermediate > 0:
        return 'intermediate'
    elif advanced == total:
        if total == 0:
            return 'ungrouped'
        else:
            return 'advanced'
    else:
        return 'reinforcement'
            

def save_groups(request,id_class):
    #Funcion de prueba que crea un nuevo grupo con datos de prueba
    g = Group()
    g.name = 'test'
    g.type = 'avanzado'
    g.start_date = timezone.now()
    g.end_date = timezone.now()
    g.kaid_student_tutor_id = 'kaid_1097501097555535353578558'
    g.save()
    return render (request,'groups.html')