from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from development.forms import ProjectForm
from django.http import JsonResponse
from django.contrib import messages
from development.models import *
from custom.utils import getnewid, getjustnewid, hash_md5, getlastid
from django.db.models import Count
from xhtml2pdf import pisa
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import Avg, Count, Min, Sum
import numpy as np
import pandas as pd
from administration.models import Year
from main.decorators import allowed_users
from employee.models import *
# report
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
import xlwt

@login_required
def project_charts_all(request):
    # currentYear = date.today().year
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    querysets = None
    labels = []
    data = []
    municipality = Municipality.objects.all()
    for m in municipality:
        querysets = Project.objects.filter(municipality=m).all().count()
        # print(querysets)
        labels.append(m.name)
        data.append(querysets)
    return JsonResponse(data={
        'labels':labels,
        'data':data,
        })

def project_charts(request,year):
    currentYear = date.today().year
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    querysets = None
    labels = []
    data = []
    municipality = Municipality.objects.all()
    for m in municipality:
        querysets = Project.objects.filter(municipality=m,year__year=year).all().count()
        # print(querysets)
        labels.append(m.name)
        data.append(querysets)
    return JsonResponse(data={
        'labels':labels,
        'data':data,
        })

@login_required
def project_charts_municipality(request,mun):
    currentYear = date.today().year
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    querysets = None
    labels = []
    data = []
    adminpost = AdministrativePost.objects.filter(municipality__id=mun)
    for ap in adminpost:
        querysets = Project.objects.filter(municipality__id=mun, administrativepost=ap.id).all().count()
        labels.append(ap.name)
        data.append(querysets)
    return JsonResponse(data={
        'labels':labels,
        'data':data,
        })

@login_required
def project_charts_municipality_year(request,mun,year):
    currentYear = date.today().year
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    querysets = None
    labels = []
    data = []
    adminpost = AdministrativePost.objects.filter(municipality__id=mun)
    for ap in adminpost:
        querysets = Project.objects.filter(municipality__id=mun, administrativepost=ap.id,year__year=year).all().count()
        labels.append(ap.name)
        data.append(querysets)
    return JsonResponse(data={
        'labels':labels,
        'data':data,
        })

@login_required
def project_charts_municipality_adminpost(request,mun,ap):
    currentYear = date.today().year
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    querysets = None
    labels = []
    data = []
    adminpost = AdministrativePost.objects.filter(municipality__id=mun)
    village = Village.objects.filter(administrativepost__id=ap)
    for v in village:
        querysets = Project.objects.filter(municipality__id=mun, administrativepost=ap, village=v.id).all().count()
        labels.append(v.name)
        data.append(querysets)
    return JsonResponse(data={
        'labels':labels,
        'data':data,
        })

@login_required
def project_charts_municipality_adminpost_year(request,mun,ap,year):
    currentYear = date.today().year
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    querysets = None
    labels = []
    data = []
    adminpost = AdministrativePost.objects.filter(municipality__id=mun)
    village = Village.objects.filter(administrativepost__id=ap)
    for v in village:
        querysets = Project.objects.filter(municipality__id=mun, administrativepost=ap, village=v.id,year__year=year).all().count()
        labels.append(v.name)
        data.append(querysets)
    return JsonResponse(data={
        'labels':labels,
        'data':data,
        })

@login_required
def activity_charts(request,year):
    currentYear = date.today().year
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    querysets = None
    labels = []
    data = []
    municipality = Municipality.objects.all()
    for m in municipality:
        querysets = Activity.objects.filter(municipality=m,year__year=year).all().count()
        # print(querysets)
        labels.append(m.name)
        data.append(querysets)
    return JsonResponse(data={
        'labels':labels,
        'data':data,
        })

@login_required
def activity_charts_all(request):
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    querysets = None
    labels = []
    data = []
    municipality = Municipality.objects.all()
    for m in municipality:
        querysets = Activity.objects.filter(municipality=m).all().count()
        # print(querysets)
        labels.append(m.name)
        data.append(querysets)
    return JsonResponse(data={
        'labels':labels,
        'data':data,
        })

@login_required
def activity_charts_municipality(request,mun):
    currentYear = date.today().year
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    querysets = None
    labels = []
    data = []
    adminpost = AdministrativePost.objects.filter(municipality__id=mun)
    for ap in adminpost:
        querysets = Activity.objects.filter(municipality__id=mun, administrativepost=ap.id).all().count()
        labels.append(ap.name)
        data.append(querysets)
    return JsonResponse(data={
        'labels':labels,
        'data':data,
        })

@login_required
def activity_charts_municipality_year(request,mun,year):
    currentYear = date.today().year
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    querysets = None
    labels = []
    data = []
    adminpost = AdministrativePost.objects.filter(municipality__id=mun)
    for ap in adminpost:
        querysets = Activity.objects.filter(municipality__id=mun, administrativepost=ap.id,year__year=year).all().count()
        labels.append(ap.name)
        data.append(querysets)
    return JsonResponse(data={
        'labels':labels,
        'data':data,
        })

@login_required
def activity_charts_municipality_adminpost(request,mun,ap):
    currentYear = date.today().year
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    querysets = None
    labels = []
    data = []
    adminpost = AdministrativePost.objects.filter(municipality__id=mun)
    village = Village.objects.filter(administrativepost__id=ap)
    for v in village:
        querysets = Activity.objects.filter(municipality__id=mun, administrativepost=ap, village=v.id).all().count()
        labels.append(v.name)
        data.append(querysets)
    return JsonResponse(data={
        'labels':labels,
        'data':data,
        })

@login_required
def activity_charts_municipality_adminpost_year(request,mun,ap,year):
    currentYear = date.today().year
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    querysets = None
    labels = []
    data = []
    adminpost = AdministrativePost.objects.filter(municipality__id=mun)
    village = Village.objects.filter(administrativepost__id=ap)
    for v in village:
        querysets = Activity.objects.filter(municipality__id=mun, administrativepost=ap, village=v.id,year__year=year).all().count()
        labels.append(v.name)
        data.append(querysets)
    return JsonResponse(data={
        'labels':labels,
        'data':data,
        })

@login_required
def report_development_dashboard(request):
    group = request.user.groups.all()[0].name
    all_municipality = Municipality.objects.all()
    all_year = Year.objects.all()
    title = f'Relatóriu Dezenvolvimentu Nasional'
    # if group == 'admin':
    project = Project.objects.count()
    activity = Activity.objects.count()

    if request.method == 'POST':
        municipality = request.POST.get('municipality')
        administrativepost = request.POST.get('administrativepost')
        village = request.POST.get('village')
        year = request.POST.get('year')
        projectFilter = None
        activityFilter = None
        projectCount = None
        activityCount = None
        mun = None
        adm = None
        vill = None
        mun1 = None
        page = None
        # year = None
        if municipality :
            mun = Municipality.objects.get(pk=municipality)
            # mun1 = mun.id
        if administrativepost :
            adm = AdministrativePost.objects.get(pk=administrativepost)
        if village:
            vill = Village.objects.get(pk=village)
        
        if municipality and administrativepost  and village and year:
            projectFilter = Project.objects.filter(municipality_id=municipality, administrativepost_id=administrativepost, village_id=village, year__year=year)
            activityFilter = Activity.objects.filter(municipality_id=municipality, administrativepost_id=administrativepost, village_id=village, year__year=year)
            projectCount = projectFilter.count()
            activityCount = activityFilter.count()
            if mun.name == 'Dili' or mun.name == 'Bobonaro' or mun.name == 'Ermera' or mun.name == 'Baucau':
                title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {mun}, Postu Administrativu {adm}, Suku {vill} iha Tinan {year}'
            elif mun.name == 'Oe-cusse':
                title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA, Postu Administrativu {adm}, Suku {vill} iha Tinan {year}'
            else:
                title = f'Relatóriu Dezenvolvimentu Munisípiu {mun}, Postu Administrativu {adm}, Suku {vill} iha Tinan {year}'
        elif municipality and administrativepost  and village:
            projectFilter = Project.objects.filter(municipality_id=municipality, administrativepost_id=administrativepost, village_id=village)
            activityFilter = Activity.objects.filter(municipality_id=municipality, administrativepost_id=administrativepost, village_id=village)
            projectCount = projectFilter.count()
            activityCount = activityFilter.count()
            if mun.name == 'Dili' or mun.name == 'Bobonaro' or mun.name == 'Ermera' or mun.name == 'Baucau':
                title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {mun}, Postu Administrativu {adm}, SuKu {vill}'
            elif mun.name == 'Oe-cusse':
                title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA, Postu Administrativu {adm}, SuKu {vill}'
            else:
                title = f'Relatóriu Dezenvolvimentu Munisípiu {mun}, Postu Administrativu {adm}, SuKu {vill}'                
        elif municipality and administrativepost and year :
            page = 'munadminpostyear'
            projectFilter = Project.objects.filter(municipality_id=municipality, administrativepost_id=administrativepost,year__year=year)
            activityFilter = Activity.objects.filter(municipality_id=municipality, administrativepost_id=administrativepost, year__year=year)
            projectCount = projectFilter.count()
            activityCount = activityFilter.count()
            if mun.name == 'Dili' or mun.name == 'Bobonaro' or mun.name == 'Ermera' or mun.name == 'Baucau':
                title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {mun}, Postu Administrativu {adm}, iha Tinan {year}'
            elif mun.name == 'Oe-cusse':
                title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA, Postu Administrativu {adm}, iha Tinan {year}'
            else:
                title = f'Relatóriu Dezenvolvimentu Munisípiu {mun}, Postu Administrativu {adm}, iha Tinan {year}'
        elif municipality and administrativepost :
            page = 'adminpost'
            projectFilter = Project.objects.filter(municipality_id=municipality, administrativepost_id=administrativepost)
            activityFilter = Activity.objects.filter(municipality_id=municipality, administrativepost_id=administrativepost)
            projectCount = projectFilter.count()
            activityCount = activityFilter.count()
            if mun.name == 'Dili' or mun.name == 'Bobonaro' or mun.name == 'Ermera' or mun.name == 'Baucau':
                title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {mun}, Postu Administrativu {adm}'
            elif mun.name == 'Oe-cusse':
                title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA, Postu Administrativu {adm}'
            else:
                title = f'Relatóriu Dezenvolvimentu Munisípiu {mun}, Postu Administrativu {adm}'
        elif municipality and year:
            page = 'munyear'
            projectFilter = Project.objects.filter(municipality_id=municipality,year__year=year)
            activityFilter = Activity.objects.filter(municipality_id=municipality,year__year=year)
            projectCount = projectFilter.count()
            activityCount = activityFilter.count()
            if mun.name == 'Dili' or mun.name == 'Bobonaro' or mun.name == 'Ermera' or mun.name == 'Baucau':
                title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {mun} iha Tinan {year}'
            elif mun.name == 'Oe-cusse':
                title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA iha Tinan {year}'
            else:
                title = f'Relatóriu Dezenvolvimentu Munisípiu {mun} iha Tinan {year}'   
        elif municipality:
            page = 'municipality'
            projectFilter = Project.objects.filter(municipality_id=municipality)
            activityFilter = Activity.objects.filter(municipality_id=municipality)
            projectCount = projectFilter.count()
            activityCount = activityFilter.count()
            if mun.name == 'Dili' or mun.name == 'Bobonaro' or mun.name == 'Ermera' or mun.name == 'Baucau':
                title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {mun}'
            elif mun.name == 'Oe-cusse':
                title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA'
            else:
                title = f'Relatóriu Dezenvolvimentu Munisípiu {mun}'
        elif year:
            page = 'year'
            projectFilter = Project.objects.filter(year__year=year)
            activityFilter = Activity.objects.filter(year__year=year)
            projectCount = projectFilter.count()
            activityCount = activityFilter.count()
            title = f'Relatóriu Dezenvolvimentu iha Tinan {year}'       
        else:
            projectFilter = Project.objects.all()
            activityFilter = Activity.objects.all()
            projectCount = projectFilter.count()
            activityCount = activityFilter.count()
            title = f'Relatóriu Dezenvolvimentu Nasional'
       
        context = {
        'title': title,
        'project_count': projectCount,
        'activity_count': activityCount, 
        'all_year':all_year,
        'municipality': all_municipality, 'activedevelopment':"active",
        'year':year,'mun':mun,'adm':adm,'vill':vill, 'page': page, 
        'municipalityid':municipality, 'adminpost':administrativepost
        }
        return render(request, 'development/dashboard.html', context)

    context = {
        'title': title,
        'project_count': project,
        'activity_count': activity,'all_year':all_year,
        'municipality': all_municipality, 'activedevelopment':"active",
    }
    return render(request, 'development/dashboard.html', context)


@login_required
def ProjectListAll(request):
    group = request.user.groups.all()[0].name
    project = Project.objects.all()
    projectCount = project.count()
    title = f'Relatóriu Dezenvolvimentu Nasional ho Total ({projectCount}) Projetus'
    context = {'objects':project, 'group':group, 'activedevelopment':"active",'title':title}
    return render(request, 'project/list.html', context)

@login_required
def ProjectListmun(request, mun):
    group = request.user.groups.all()[0].name
    municipality = get_object_or_404(Municipality, id=mun)
    project = Project.objects.filter(municipality=municipality)
    projectCount = project.count()
    if municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera' or municipality.name == 'Baucau':
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality} ho Total ({projectCount}) Projetus'
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu {municipality} ho Total ({projectCount}) Projetus'
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality} ho Total ({projectCount}) Projetus'
    context = {'objects':project, 'group':group, 'activedevelopment':"active",'title':title,'municipality':municipality}
    return render(request, 'project/list.html', context)

@login_required
def ProjectListyear(request, year):
    group = request.user.groups.all()[0].name
    year_today = date.today().year
    year = get_object_or_404(Year, year=year)
    project = Project.objects.filter(year=year)
    projectCount = project.count()
    title = f'Relatóriu Dezenvolvimentu iha  {year} ho Total ({projectCount}) Projetus'
    context = {'objects':project, 'group':group, 'activedevelopment':"active",'title':title,'year':year}
    return render(request, 'project/list.html', context)

@login_required
def ProjectListmunyear(request, mun, year):
    group = request.user.groups.all()[0].name
    municipality = get_object_or_404(Municipality, id=mun)
    year = get_object_or_404(Year, year=year)
    project = Project.objects.filter(municipality=municipality, year=year)
    projectCount = project.count()
    if municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera' or municipality.name == 'Baucau':
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality} iha Tinan {year} ho Total ({projectCount}) Projetus'  
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA iha Tinan {year} ho Total ({projectCount}) Projetus'  
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality} iha Tinan {year} ho Total ({projectCount}) Projetus'  
    context = {'objects':project, 'group':group, 'activedevelopment':"active",'title':title,'municipality':municipality,
    'year':year}
    return render(request, 'project/list.html', context)

@login_required
def ProjectListmunpost(request, mun, post):
    group = request.user.groups.all()[0].name
    municipality = get_object_or_404(Municipality, id=mun)
    post = get_object_or_404(AdministrativePost, id=post)
    project = Project.objects.filter(municipality=municipality, administrativepost=post)
    projectCount = project.count()
    if municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera' or municipality.name == 'Baucau':
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality} no Postu {post} ho Total ({projectCount}) Projetus'  
    elif municipality == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA no Postu {post} ho Total ({projectCount}) Projetus'  
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality} no Postu {post} ho Total ({projectCount}) Projetus'  
    context = {'objects':project,'activedevelopment':"active",
    'municipality':municipality,'group':group, 'post':post,'title':title}
    return render(request, 'project/list.html', context)

@login_required
def ProjectListmunpostyear(request, mun, post, year):
    group = request.user.groups.all()[0].name
    municipality = get_object_or_404(Municipality, id=mun)
    post = get_object_or_404(AdministrativePost, id=post)
    year = get_object_or_404(Year, year=year)
    project = Project.objects.filter(municipality=municipality, administrativepost=post, year=year)
    projectCount = project.count()
    if municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera' or municipality.name == 'Baucau':
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality} no Postu {post} iha Tinan {year} ho Total ({projectCount}) Projetus'  
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA no Postu {post} iha Tinan {year} ho Total ({projectCount}) Projetus'  
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality} no Postu {post} iha Tinan {year} ho Total ({projectCount}) Projetus'  
    context = {'objects':project,'activedevelopment':"active",'title':title,'municipality':municipality,
    'post':post,'year':year,'group':group}
    return render(request, 'project/list.html', context)

@login_required
def ProjectListmunpostvill(request, mun, post, village):
    group = request.user.groups.all()[0].name
    municipality = get_object_or_404(Municipality, id=mun)
    post = get_object_or_404(AdministrativePost, id=post)
    village = get_object_or_404(Village, id=village)
    project = Project.objects.filter(municipality=municipality, administrativepost=post, village=village)
    projectCount = project.count()
    if municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera' or municipality.name == 'Baucau':
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality}, Postu {post} no Suku {village} ho Total ({projectCount}) Projetus'
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA, Postu {post} no Suku {village} ho Total ({projectCount}) Projetus'
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality}, Postu {post} no Suku {village} ho Total ({projectCount}) Projetus'
    context = {'objects':project,'activedevelopment':"active",
    'title':title,'municipality':municipality,'post':post,'village':village,'group':group}
    return render(request, 'project/list.html', context)

@login_required
def ProjectListmunpostvillyear(request, mun, post, village, year):
    group = request.user.groups.all()[0].name
    municipality = get_object_or_404(Municipality, id=mun)
    post = get_object_or_404(AdministrativePost, id=post)
    village = get_object_or_404(Village, id=village)
    year = get_object_or_404(Year, year=year)
    project = Project.objects.filter(municipality=municipality, administrativepost=post, village=village, year=year)
    projectCount = project.count()
    if municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera' or municipality.name == 'Baucau':
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality}, Postu {post} no Suku {village} iha {year} ho Total ({projectCount}) Projetus'
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA, Postu {post} no Suku {village} iha {year} ho Total ({projectCount}) Projetus'
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality}, Postu {post} no Suku {village} iha {year} ho Total ({projectCount}) Projetus'
    context = {
    'objects':project,
    'title':title,'municipality':municipality,'post':post,'village':village,
    'year':year,'activedevelopment':"active",'group':group
    }
    return render(request, 'project/list.html', context)


@login_required
def ActivityListmun(request, mun):
    group = request.user.groups.all()[0].name
    municipality = get_object_or_404(Municipality, id=mun)
    activity = Activity.objects.filter(municipality=municipality)
    activityCount = activity.count()
    if municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera' or municipality.name == 'Baucau':
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality} ho Total ({activityCount}) Atividades'
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA ho Total ({activityCount}) Atividades'
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality} ho Total ({activityCount}) Atividades'
    context = {'objects':activity,'group':group, 'activedevelopment':"active",'title':title,'municipality':municipality}
    return render(request, 'activity/list.html', context)

@login_required
def ActivityListAll(request):
    group = request.user.groups.all()[0].name
    activity = Activity.objects.all()
    activityCount = activity.count()
    title = f'Relatóriu Dezenvolvimentu Nasional ho Total ({activityCount}) Atividades'
    context = {'objects':activity,'group':group, 'activedevelopment':"active",'title':title}
    return render(request, 'activity/list.html', context)

@login_required
def ActivityListyear(request, year):
    group = request.user.groups.all()[0].name
    year = get_object_or_404(Year, year=year)
    activity = Activity.objects.filter(year=year)
    activityCount = activity.count()
    title = f'Relatóriu Dezenvolvimentu iha Tinan {year} ho Total ({activityCount}) Atividades'
    context = {'objects':activity,'group':group, 'activedevelopment':"active",'title':title,'year':year}
    return render(request, 'activity/list.html', context)

@login_required
def ActivityListmunyear(request, mun, year):
    group = request.user.groups.all()[0].name
    municipality = get_object_or_404(Municipality, id=mun)
    year = get_object_or_404(Year, year=year)
    activity = Activity.objects.filter(municipality=municipality, year=year)
    activityCount = activity.count()
    if municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera' or municipality.name == 'Baucau':
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality} iha Tinan {year} ho Total ({activityCount}) Atividades'
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autonomu RAEOA iha Tinan {year} ho Total ({activityCount}) Atividades'
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality} iha Tinan {year} ho Total ({activityCount}) Atividades'
    context = {'objects':activity,'group':group, 'activedevelopment':"active",'title':title,'municipality':municipality,
    'year':year}
    return render(request, 'activity/list.html', context)

@login_required
def ActivityListmunyear(request, mun, year):
    group = request.user.groups.all()[0].name
    municipality = get_object_or_404(Municipality, id=mun)
    year = get_object_or_404(Year, year=year)
    activity = Activity.objects.filter(municipality=municipality, year=year)
    activityCount = activity.count()
    if municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera' or municipality.name == 'Baucau':
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality} iha Tinan {year} ho Total ({activityCount}) Atividades'
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA iha Tinan {year} ho Total ({activityCount}) Atividades'
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality} iha Tinan {year} ho Total ({activityCount}) Atividades'
    context = {'objects':activity,'group':group, 'activedevelopment':"active",'title':title,'municipality':municipality,
    'year':year}
    return render(request, 'activity/list.html', context)

@login_required
def ActivityListmunpost(request, mun, post):
    group = request.user.groups.all()[0].name
    municipality = get_object_or_404(Municipality, id=mun)
    post = get_object_or_404(AdministrativePost, id=post)
    activity = Activity.objects.filter(municipality=municipality, administrativepost=post)
    activityCount = activity.count()
    if municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera' or municipality.name == 'Baucau':
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality} no Postu {post} ho Total ({activityCount}) Atividades'
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA no Postu {post} ho Total ({activityCount}) Atividades'
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality} no Postu {post} ho Total ({activityCount}) Atividades'
    context = {'objects':activity,'group':group, 'activedevelopment':"active",'title':title,'municipality':municipality,
    'post':post}
    return render(request, 'activity/list.html', context)

@login_required
def ActivityListmunpostyear(request, mun, post, year):
    group = request.user.groups.all()[0].name
    municipality = get_object_or_404(Municipality, id=mun)
    post = get_object_or_404(AdministrativePost, id=post)
    year = get_object_or_404(Year, year=year)
    activity = Activity.objects.filter(municipality=municipality, administrativepost=post, year=year)
    activityCount = activity.count()
    if municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera' or municipality.name == 'Baucau':
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality} no Postu {post} iha Tinan {year} ho Total ({activityCount}) Atividades'
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA no Postu {post} iha Tinan {year} ho Total ({activityCount}) Atividades'
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality} no Postu {post} iha Tinan {year} ho Total ({activityCount}) Atividades'
    context = {'objects':activity,'group':group, 'activedevelopment':"active",'title':title,'municipality':municipality,
    'post':post,'year':year}
    return render(request, 'activity/list.html', context)

@login_required
def ActivityListmunpostvillage(request, mun, post, village):
    group = request.user.groups.all()[0].name
    municipality = get_object_or_404(Municipality, id=mun)
    post = get_object_or_404(AdministrativePost, id=post)
    village = get_object_or_404(Village, id=village)
    activity = Activity.objects.filter(municipality=municipality, administrativepost=post, village=village)
    activityCount = activity.count()
    if municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera' or municipality.name == 'Baucau':
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality}, Postu {post} no Suku {village} ho Total ({activityCount}) Atividades'
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA, Postu {post} no Suku {village} ho Total ({activityCount}) Atividades'
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality}, Postu {post} no Suku {village} ho Total ({activityCount}) Atividades'
    context = {'objects':activity,'group':group, 'activedevelopment':"active",'title':title,'municipality':municipality,
    'post':post,'village':village}
    return render(request, 'activity/list.html', context)

@login_required
def ActivityListmunpostvillageyear(request, mun, post, village, year):
    group = request.user.groups.all()[0].name
    municipality = get_object_or_404(Municipality, id=mun)
    post = get_object_or_404(AdministrativePost, id=post)
    village = get_object_or_404(Village, id=village)
    year = get_object_or_404(Year, year=year)
    activity = Activity.objects.filter(municipality=municipality, administrativepost=post, village=village, year=year)
    activityCount = activity.count()
    if municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera' or municipality.name == 'Baucau':
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality}, Postu {post} no Suku {village} iha Tinan {year} ho Total ({activityCount}) Atividades'
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA, Postu {post} no Suku {village} iha Tinan {year} ho Total ({activityCount}) Atividades'
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality}, Postu {post} no Suku {village} iha Tinan {year} ho Total ({activityCount}) Atividades'
    context = {'objects':activity,'group':group, 'activedevelopment':"active",'title':title,'municipality':municipality,
    'post':post,'village':village,'year':year}
    return render(request, 'activity/list.html', context)

@login_required
def ReportProject6(request, mun, post, village, year):
    empuser = None
    employee = None
    # EmployeeUser.objects.get(user = request.user).exists():
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    municipality = get_object_or_404(Municipality, id=mun)
    post = get_object_or_404(AdministrativePost, id=post)
    village = get_object_or_404(Village, id=village)
    year = get_object_or_404(Year, year=year)
    project = Project.objects.filter(municipality=mun, administrativepost=post, village=village, year=year)
    fNational = FundNational.objects.all()
    fMunicipality = FundMunicipality.objects.all()
    fOng = FundONG.objects.all()
    fVolunteer = FundVolunteer.objects.all()
    total = []
    for pro in project:
        fn,fm,fo,fv,total_fund =   [],[],[],[], []
        fn = FundNational.objects.filter(project=pro.id).aggregate(Sum('national_amount'))
        fm = FundMunicipality.objects.filter(project=pro.id).aggregate(Sum('municipality_amount'))
        fo = FundONG.objects.filter(project=pro.id).aggregate(Sum('ong_amount'))
        fv = FundVolunteer.objects.filter(project=pro.id).aggregate(Sum('volunteer_amount'))
        if fn['national_amount__sum']:
            total_fund.append(fn['national_amount__sum'])
        if fm['municipality_amount__sum']:
            total_fund.append(fm['municipality_amount__sum'])
        if fo['ong_amount__sum']:
            total_fund.append(fo['ong_amount__sum'])
        if fv['volunteer_amount__sum']:
            total_fund.append(fv['volunteer_amount__sum'])
        total.append(np.sum(total_fund))
    df1 = pd.DataFrame(project)
    df1['total_amount'] = total
    if municipality.name == 'Baucau' or municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera':
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality}, Postu {post} no Suku {village} iha Tinan {year}'
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA, Postu {post} no Suku {village} iha Tinan {year}'
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality}, Postu {post} no Suku {village} iha Tinan {year}'
    data = {
    'title': title, 
    'objects': df1, 
    'project':project,
    'employee': employee, 
    'page':"excelproject",
    'fNational': fNational, 
    'fMunicipality': fMunicipality, 
    'fOng':fOng, 
    'fVolunteer':fVolunteer, 
    'total_amount_national':total, 'municipality':municipality,'post':post,'village':village,
    'year':year,'activedevelopment':"active"}
    return render(request, 'development/print/project.html', data)

@login_required
def ReportProject7(request, year):
    empuser = None
    employee = None
    # EmployeeUser.objects.get(user = request.user).exists():
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    year = get_object_or_404(Year, year=year)
    project = Project.objects.filter(year=year)
    fNational = FundNational.objects.all()
    fMunicipality = FundMunicipality.objects.all()
    fOng = FundONG.objects.all()
    fVolunteer = FundVolunteer.objects.all()
    total = []
    for pro in project:
        fn,fm,fo,fv,total_fund = [],[],[],[], []
        fn = FundNational.objects.filter(project=pro.id).aggregate(Sum('national_amount'))
        fm = FundMunicipality.objects.filter(project=pro.id).aggregate(Sum('municipality_amount'))
        fo = FundONG.objects.filter(project=pro.id).aggregate(Sum('ong_amount'))
        fv = FundVolunteer.objects.filter(project=pro.id).aggregate(Sum('volunteer_amount'))
        if fn['national_amount__sum']:
            total_fund.append(fn['national_amount__sum'])
        if fm['municipality_amount__sum']:
            total_fund.append(fm['municipality_amount__sum'])
        if fo['ong_amount__sum']:
            total_fund.append(fo['ong_amount__sum'])
        if fv['volunteer_amount__sum']:
            total_fund.append(fv['volunteer_amount__sum'])
        total.append(np.sum(total_fund))
    df1 = pd.DataFrame(project)
    df1['total_amount'] = total
    title = f'Relatóriu Dezenvolvimentu iha Tinan {year}'
    data = {
    'title': title, 
    'objects': df1, 
    'project':project,
    'employee': employee, 
    'fNational': fNational, 
    'fMunicipality': fMunicipality, 
    'fOng':fOng, 
    'fVolunteer':fVolunteer, 
    'page':"excelproject",
    'total_amount_national':total,'year':year,'activedevelopment':"active"}
    return render(request, 'development/print/project.html', data)

@login_required
def ReportProject5(request, mun, post, village):
    empuser = None
    employee = None
    # EmployeeUser.objects.get(user = request.user).exists():
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    municipality = get_object_or_404(Municipality, id=mun)
    post = get_object_or_404(AdministrativePost, id=post)
    village = get_object_or_404(Village, id=village)
    project = Project.objects.filter(municipality=mun, administrativepost=post, village=village)
    fNational = FundNational.objects.all()
    fMunicipality = FundMunicipality.objects.all()
    fOng = FundONG.objects.all()
    fVolunteer = FundVolunteer.objects.all()
    total = []
    for pro in project:
        fn,fm,fo,fv,total_fund =   [],[],[],[], []
        fn = FundNational.objects.filter(project=pro.id).aggregate(Sum('national_amount'))
        fm = FundMunicipality.objects.filter(project=pro.id).aggregate(Sum('municipality_amount'))
        fo = FundONG.objects.filter(project=pro.id).aggregate(Sum('ong_amount'))
        fv = FundVolunteer.objects.filter(project=pro.id).aggregate(Sum('volunteer_amount'))
        if fn['national_amount__sum']:
            total_fund.append(fn['national_amount__sum'])
        if fm['municipality_amount__sum']:
            total_fund.append(fm['municipality_amount__sum'])
        if fo['ong_amount__sum']:
            total_fund.append(fo['ong_amount__sum'])
        if fv['volunteer_amount__sum']:
            total_fund.append(fv['volunteer_amount__sum'])
        total.append(np.sum(total_fund))
    df1 = pd.DataFrame(project)
    df1['total_amount'] = total
    if municipality.name == 'Baucau' or municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera':
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality}, Postu {post} no Suku {village}'
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA, Postu {post} no Suku {village}'
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality}, Postu {post} no Suku {village}'
    data = {
    'title': title, 
    'objects': df1, 
    'project':project,
    'employee': employee, 
    'page':"excelproject",
    'fNational': fNational, 
    'fMunicipality': fMunicipality, 
    'fOng':fOng, 
    'fVolunteer':fVolunteer, 'activedevelopment':"active",
    'total_amount_national':total, 'municipality':municipality,'post':post,'village':village}
    return render(request, 'development/print/project.html', data)


@login_required
def ReportProject4(request, mun, post, year):
    empuser = None
    employee = None
    # EmployeeUser.objects.get(user = request.user).exists():
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    municipality = get_object_or_404(Municipality, id=mun)
    post = get_object_or_404(AdministrativePost, id=post)
    year = get_object_or_404(Year, year=year)
    project = Project.objects.filter(municipality=mun, administrativepost=post, year=year)
    fNational = FundNational.objects.all()
    fMunicipality = FundMunicipality.objects.all()
    fOng = FundONG.objects.all()
    fVolunteer = FundVolunteer.objects.all()
    total = []
    for pro in project:
        fn,fm,fo,fv,total_fund =   [],[],[],[], []
        fn = FundNational.objects.filter(project=pro.id).aggregate(Sum('national_amount'))
        fm = FundMunicipality.objects.filter(project=pro.id).aggregate(Sum('municipality_amount'))
        fo = FundONG.objects.filter(project=pro.id).aggregate(Sum('ong_amount'))
        fv = FundVolunteer.objects.filter(project=pro.id).aggregate(Sum('volunteer_amount'))
        if fn['national_amount__sum']:
            total_fund.append(fn['national_amount__sum'])
        if fm['municipality_amount__sum']:
            total_fund.append(fm['municipality_amount__sum'])
        if fo['ong_amount__sum']:
            total_fund.append(fo['ong_amount__sum'])
        if fv['volunteer_amount__sum']:
            total_fund.append(fv['volunteer_amount__sum'])
        total.append(np.sum(total_fund))
    df1 = pd.DataFrame(project)
    df1['total_amount'] = total
    if municipality.name == 'Baucau' or municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera':
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality}, Postu {post} iha Tinan {year}'
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA, Postu {post} iha Tinan {year}'
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality}, Postu {post} iha Tinan {year}'
    data = {
    'title': title, 
    'objects': df1, 
    'project':project,
    'employee': employee,
    'page':"excelproject",
    'fNational': fNational, 
    'fMunicipality': fMunicipality, 
    'fOng':fOng, 
    'fVolunteer':fVolunteer, 'activedevelopment':"active",
    'total_amount_national':total, 'municipality':municipality,'post':post,'year':year}
    return render(request, 'development/print/project.html', data)


@login_required
def ReportProject3(request, mun, post):
    empuser = None
    employee = None
    # EmployeeUser.objects.get(user = request.user).exists():
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    municipality = get_object_or_404(Municipality, id=mun)
    post = get_object_or_404(AdministrativePost, id=post)
    project = Project.objects.filter(municipality=mun, administrativepost=post)
    fNational = FundNational.objects.all()
    fMunicipality = FundMunicipality.objects.all()
    fOng = FundONG.objects.all()
    fVolunteer = FundVolunteer.objects.all()
    total = []
    for pro in project:
        fn,fm,fo,fv,total_fund =   [],[],[],[], []
        fn = FundNational.objects.filter(project=pro.id).aggregate(Sum('national_amount'))
        fm = FundMunicipality.objects.filter(project=pro.id).aggregate(Sum('municipality_amount'))
        fo = FundONG.objects.filter(project=pro.id).aggregate(Sum('ong_amount'))
        fv = FundVolunteer.objects.filter(project=pro.id).aggregate(Sum('volunteer_amount'))
        if fn['national_amount__sum']:
            total_fund.append(fn['national_amount__sum'])
        if fm['municipality_amount__sum']:
            total_fund.append(fm['municipality_amount__sum'])
        if fo['ong_amount__sum']:
            total_fund.append(fo['ong_amount__sum'])
        if fv['volunteer_amount__sum']:
            total_fund.append(fv['volunteer_amount__sum'])
        total.append(np.sum(total_fund))
    df1 = pd.DataFrame(project)
    df1['total_amount'] = total
    if municipality.name == 'Baucau' or municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera':
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality} no Postu {post}'
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA no Postu {post}'
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality} no Postu {post}'
    data = {
    'title': title, 
    'objects': df1, 
    'project':project,
    'employee': employee, 
    'page':"excelproject",
    'fNational': fNational, 
    'fMunicipality': fMunicipality, 
    'fOng':fOng, 
    'fVolunteer':fVolunteer, 'activedevelopment':"active",
    'total_amount_national':total, 'municipality':municipality,'post':post}
    return render(request, 'development/print/project.html', data)

@login_required
def ReportProject2(request, mun, year):
    empuser = None
    employee = None
    # EmployeeUser.objects.get(user = request.user).exists():
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    municipality = get_object_or_404(Municipality, id=mun)
    year = get_object_or_404(Year, year=year)
    project = Project.objects.filter(municipality=mun, year=year)
    fNational = FundNational.objects.all()
    fMunicipality = FundMunicipality.objects.all()
    fOng = FundONG.objects.all()
    fVolunteer = FundVolunteer.objects.all()
    total = []
    for pro in project:
        fn,fm,fo,fv,total_fund =   [],[],[],[], []
        fn = FundNational.objects.filter(project=pro.id).aggregate(Sum('national_amount'))
        fm = FundMunicipality.objects.filter(project=pro.id).aggregate(Sum('municipality_amount'))
        fo = FundONG.objects.filter(project=pro.id).aggregate(Sum('ong_amount'))
        fv = FundVolunteer.objects.filter(project=pro.id).aggregate(Sum('volunteer_amount'))
        if fn['national_amount__sum']:
            total_fund.append(fn['national_amount__sum'])
        if fm['municipality_amount__sum']:
            total_fund.append(fm['municipality_amount__sum'])
        if fo['ong_amount__sum']:
            total_fund.append(fo['ong_amount__sum'])
        if fv['volunteer_amount__sum']:
            total_fund.append(fv['volunteer_amount__sum'])
        total.append(np.sum(total_fund))
    df1 = pd.DataFrame(project)
    df1['total_amount'] = total
    if municipality.name == 'Baucau' or municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera':
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality} iha Tinan {year}'
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA iha Tinan {year}'
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality} iha Tinan {year}'
    data = {
    'title': title, 
    'objects': df1, 
    'project':project,
    'employee': employee, 
    'fNational': fNational, 
    'page':"excelproject",
    'fMunicipality': fMunicipality, 
    'fOng':fOng, 
    'fVolunteer':fVolunteer, 'activedevelopment':"active",
    'total_amount_national':total, 'municipality':municipality,'year':year}
    return render(request, 'development/print/project.html', data)

@login_required
def ReportProject1(request, mun):
    empuser = None
    employee = None
    # EmployeeUser.objects.get(user = request.user).exists():
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    municipality = get_object_or_404(Municipality, id=mun)
    project = Project.objects.filter(municipality=mun)
    fNational = FundNational.objects.all()
    fMunicipality = FundMunicipality.objects.all()
    fOng = FundONG.objects.all()
    fVolunteer = FundVolunteer.objects.all()
    total = []
    for pro in project:
        fn,fm,fo,fv,total_fund =   [],[],[],[], []
        fn = FundNational.objects.filter(project=pro.id).aggregate(Sum('national_amount'))
        fm = FundMunicipality.objects.filter(project=pro.id).aggregate(Sum('municipality_amount'))
        fo = FundONG.objects.filter(project=pro.id).aggregate(Sum('ong_amount'))
        fv = FundVolunteer.objects.filter(project=pro.id).aggregate(Sum('volunteer_amount'))
        if fn['national_amount__sum']:
            total_fund.append(fn['national_amount__sum'])
        if fm['municipality_amount__sum']:
            total_fund.append(fm['municipality_amount__sum'])
        if fo['ong_amount__sum']:
            total_fund.append(fo['ong_amount__sum'])
        if fv['volunteer_amount__sum']:
            total_fund.append(fv['volunteer_amount__sum'])
        total.append(np.sum(total_fund))
    df1 = pd.DataFrame(project)
    df1['total_amount'] = total
    if municipality.name == 'Baucau' or municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera':
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality}'
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA'
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality}'
    data = {
    'title': title, 
    'objects': df1, 
    'project':project,
    'employee': employee, 
    'fNational': fNational, 
    'fMunicipality': fMunicipality, 
    'fOng':fOng, 
    'page':"excelproject",
    'fVolunteer':fVolunteer, 'activedevelopment':"active",
    'total_amount_national':total, 'municipality':municipality}
    return render(request, 'development/print/project.html', data)

@login_required
def ReportProjectAll(request):
    empuser = None
    employee = None
    # EmployeeUser.objects.get(user = request.user).exists():
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    project = Project.objects.all()
    fNational = FundNational.objects.all()
    fMunicipality = FundMunicipality.objects.all()
    fOng = FundONG.objects.all()
    fVolunteer = FundVolunteer.objects.all()
    total = []
    for pro in project:
        fn,fm,fo,fv,total_fund =   [],[],[],[], []
        fn = FundNational.objects.filter(project=pro.id).aggregate(Sum('national_amount'))
        fm = FundMunicipality.objects.filter(project=pro.id).aggregate(Sum('municipality_amount'))
        fo = FundONG.objects.filter(project=pro.id).aggregate(Sum('ong_amount'))
        fv = FundVolunteer.objects.filter(project=pro.id).aggregate(Sum('volunteer_amount'))
        if fn['national_amount__sum']:
            total_fund.append(fn['national_amount__sum'])
        if fm['municipality_amount__sum']:
            total_fund.append(fm['municipality_amount__sum'])
        if fo['ong_amount__sum']:
            total_fund.append(fo['ong_amount__sum'])
        if fv['volunteer_amount__sum']:
            total_fund.append(fv['volunteer_amount__sum'])
        total.append(np.sum(total_fund))
    df1 = pd.DataFrame(project)
    df1['total_amount'] = total
    title = f'Relatóriu Dezenvolvimentu Nasional'
    data = {
    'title': title, 
    'objects': df1, 
    'project':project,
    'employee': employee, 
    'fNational': fNational, 
    'fMunicipality': fMunicipality, 
    'fOng':fOng, 
    'page':"excelproject",
    'fVolunteer':fVolunteer, 'activedevelopment':"active",
    'total_amount_national':total}
    return render(request, 'development/print/project.html', data)


# REPORT EXCEL ATIVIDADE

@login_required
def ReportActivityAll(request):
    empuser = None
    employee = None
    # EmployeeUser.objects.get(user = request.user).exists():
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    activity = Activity.objects.all()
    fNational = FundNational.objects.all()
    fMunicipality = FundMunicipality.objects.all()
    fCommunity = FundCommunityContribute.objects.all()
    fAgency = FundAgency.objects.all()
    total = []
    for ac in activity:
        fn,fm,fc,fa,total_fund =   [],[],[],[], []
        fn = FundNational.objects.filter(activity=ac.id).aggregate(Sum('national_amount'))
        fm = FundMunicipality.objects.filter(activity=ac.id).aggregate(Sum('municipality_amount'))
        fc = FundCommunityContribute.objects.filter(activity=ac.id).aggregate(Sum('communitycontribute_amount'))
        fa = FundAgency.objects.filter(activity=ac.id).aggregate(Sum('agency_amount'))
        if fn['national_amount__sum']:
            total_fund.append(fn['national_amount__sum'])
        if fm['municipality_amount__sum']:
            total_fund.append(fm['municipality_amount__sum'])
        if fc['communitycontribute_amount__sum']:
            total_fund.append(fc['communitycontribute_amount__sum'])
        if fa['agency_amount__sum']:
            total_fund.append(fa['agency_amount__sum'])
        total.append(np.sum(total_fund))
    df1 = pd.DataFrame(activity)
    df1['total_amount'] = total   
    title = f'Relatóriu Dezenvolvimentu Nasional' 
    data = {
    'title': title,
    'objects': df1, 
    'employee': employee,
    'page':"excelactivity",
    'fNational': fNational, 'fMunicipality': fMunicipality, 'fCommunity':fCommunity, 'fAgency':fAgency,
    'total_amount_national':total}
    return render(request, 'development/print/activity.html', data)


@login_required
def ReportActivity1(request, mun):
    empuser = None
    employee = None
    # EmployeeUser.objects.get(user = request.user).exists():
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    municipality = get_object_or_404(Municipality, id=mun)
    activity = Activity.objects.filter(municipality=municipality)
    fNational = FundNational.objects.all()
    fMunicipality = FundMunicipality.objects.all()
    fCommunity = FundCommunityContribute.objects.all()
    fAgency = FundAgency.objects.all()
    total = []
    for ac in activity:
        fn,fm,fc,fa,total_fund =   [],[],[],[], []
        fn = FundNational.objects.filter(activity=ac.id).aggregate(Sum('national_amount'))
        fm = FundMunicipality.objects.filter(activity=ac.id).aggregate(Sum('municipality_amount'))
        fc = FundCommunityContribute.objects.filter(activity=ac.id).aggregate(Sum('communitycontribute_amount'))
        fa = FundAgency.objects.filter(activity=ac.id).aggregate(Sum('agency_amount'))
        if fn['national_amount__sum']:
            total_fund.append(fn['national_amount__sum'])
        if fm['municipality_amount__sum']:
            total_fund.append(fm['municipality_amount__sum'])
        if fc['communitycontribute_amount__sum']:
            total_fund.append(fc['communitycontribute_amount__sum'])
        if fa['agency_amount__sum']:
            total_fund.append(fa['agency_amount__sum'])
        total.append(np.sum(total_fund))
    df1 = pd.DataFrame(activity)
    df1['total_amount'] = total
    if municipality.name == 'Baucau' or municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera':      
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality}' 
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA' 
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality}' 
    data = {
    'title': title,'objects': df1,
    'fNational': fNational, 
    'fMunicipality': fMunicipality, 
    'fCommunity':fCommunity, 
    'employee': employee,
    'page':"excelactivity",
    'fAgency':fAgency,
    'total_amount_national':total, 'municipality':municipality}
    return render(request, 'development/print/activity.html', data)

@login_required
def ReportActivity7(request, year):
    empuser = None
    employee = None
    # EmployeeUser.objects.get(user = request.user).exists():
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    year = get_object_or_404(Year, year=year)
    activity = Activity.objects.filter(year=year)
    fNational = FundNational.objects.all()
    fMunicipality = FundMunicipality.objects.all()
    fCommunity = FundCommunityContribute.objects.all()
    fAgency = FundAgency.objects.all()
    total = []
    for ac in activity:
        fn,fm,fc,fa,total_fund =   [],[],[],[], []
        fn = FundNational.objects.filter(activity=ac.id).aggregate(Sum('national_amount'))
        fm = FundMunicipality.objects.filter(activity=ac.id).aggregate(Sum('municipality_amount'))
        fc = FundCommunityContribute.objects.filter(activity=ac.id).aggregate(Sum('communitycontribute_amount'))
        fa = FundAgency.objects.filter(activity=ac.id).aggregate(Sum('agency_amount'))
        if fn['national_amount__sum']:
            total_fund.append(fn['national_amount__sum'])
        if fm['municipality_amount__sum']:
            total_fund.append(fm['municipality_amount__sum'])
        if fc['communitycontribute_amount__sum']:
            total_fund.append(fc['communitycontribute_amount__sum'])
        if fa['agency_amount__sum']:
            total_fund.append(fa['agency_amount__sum'])
        total.append(np.sum(total_fund))
    df1 = pd.DataFrame(activity)
    df1['total_amount'] = total   
    title = f'Relatóriu Dezenvolvimentu iha Tinan {year}' 
    data = {
    'title': title,
    'objects': df1, 
    'employee': employee,
    'page':"excelactivity",
    'fNational': fNational, 'fMunicipality': fMunicipality, 'fCommunity':fCommunity, 'fAgency':fAgency,
    'total_amount_national':total, 'year':year}
    return render(request, 'development/print/activity.html', data)

@login_required
def ReportActivity2(request, mun, year):
    empuser = None
    employee = None
    # EmployeeUser.objects.get(user = request.user).exists():
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    municipality = get_object_or_404(Municipality, id=mun)
    year = get_object_or_404(Year, year=year)
    activity = Activity.objects.filter(municipality=municipality, year=year)
    fNational = FundNational.objects.all()
    fMunicipality = FundMunicipality.objects.all()
    fCommunity = FundCommunityContribute.objects.all()
    fAgency = FundAgency.objects.all()
    total = []
    for ac in activity:
        fn,fm,fc,fa,total_fund =   [],[],[],[], []
        fn = FundNational.objects.filter(activity=ac.id).aggregate(Sum('national_amount'))
        fm = FundMunicipality.objects.filter(activity=ac.id).aggregate(Sum('municipality_amount'))
        fc = FundCommunityContribute.objects.filter(activity=ac.id).aggregate(Sum('communitycontribute_amount'))
        fa = FundAgency.objects.filter(activity=ac.id).aggregate(Sum('agency_amount'))
        if fn['national_amount__sum']:
            total_fund.append(fn['national_amount__sum'])
        if fm['municipality_amount__sum']:
            total_fund.append(fm['municipality_amount__sum'])
        if fc['communitycontribute_amount__sum']:
            total_fund.append(fc['communitycontribute_amount__sum'])
        if fa['agency_amount__sum']:
            total_fund.append(fa['agency_amount__sum'])
        total.append(np.sum(total_fund))
    df1 = pd.DataFrame(activity)
    df1['total_amount'] = total
    if municipality.name == 'Baucau' or municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera':   
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality} iha Tinan {year}' 
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA iha Tinan {year}' 
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality} iha Tinan {year}' 
    data = {
    'title': title,
    'objects': df1, 
    'employee': employee,
    'page':"excelactivity",
    'fNational': fNational, 'fMunicipality': fMunicipality, 'fCommunity':fCommunity, 'fAgency':fAgency,
    'total_amount_national':total, 'municipality':municipality,'year':year}
    return render(request, 'development/print/activity.html', data)

@login_required
def ReportActivity3(request, mun, post):
    empuser = None
    employee = None
    # EmployeeUser.objects.get(user = request.user).exists():
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    municipality = get_object_or_404(Municipality, id=mun)
    post = get_object_or_404(AdministrativePost, id=post)
    activity = Activity.objects.filter(municipality=municipality, administrativepost=post)
    fNational = FundNational.objects.all()
    fMunicipality = FundMunicipality.objects.all()
    fCommunity = FundCommunityContribute.objects.all()
    fAgency = FundAgency.objects.all()
    total = []
    for ac in activity:
        fn,fm,fc,fa,total_fund =   [],[],[],[], []
        fn = FundNational.objects.filter(activity=ac.id).aggregate(Sum('national_amount'))
        fm = FundMunicipality.objects.filter(activity=ac.id).aggregate(Sum('municipality_amount'))
        fc = FundCommunityContribute.objects.filter(activity=ac.id).aggregate(Sum('communitycontribute_amount'))
        fa = FundAgency.objects.filter(activity=ac.id).aggregate(Sum('agency_amount'))
        if fn['national_amount__sum']:
            total_fund.append(fn['national_amount__sum'])
        if fm['municipality_amount__sum']:
            total_fund.append(fm['municipality_amount__sum'])
        if fc['communitycontribute_amount__sum']:
            total_fund.append(fc['communitycontribute_amount__sum'])
        if fa['agency_amount__sum']:
            total_fund.append(fa['agency_amount__sum'])
        total.append(np.sum(total_fund))
    df1 = pd.DataFrame(activity)
    df1['total_amount'] = total 
    if municipality.name == 'Baucau' or municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera':     
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality} no Postu {post}' 
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA no Postu {post}' 
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality} no Postu {post}' 
    data = {'title': title,
    'objects': df1, 
    'employee': employee,
    'page':"excelactivity",
    'fNational': fNational, 'fMunicipality': fMunicipality, 'fCommunity':fCommunity, 'fAgency':fAgency,
    'total_amount_national':total, 'municipality':municipality,'post':post
            }
    return render(request, 'development/print/activity.html', data)

@login_required
def ReportActivity4(request, mun, post, year):
    empuser = None
    employee = None
    # EmployeeUser.objects.get(user = request.user).exists():
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    municipality = get_object_or_404(Municipality, id=mun)
    post = get_object_or_404(AdministrativePost, id=post)
    year = get_object_or_404(Year, year=year)
    activity = Activity.objects.filter(municipality=municipality, administrativepost=post, year=year)
    fNational = FundNational.objects.all()
    fMunicipality = FundMunicipality.objects.all()
    fCommunity = FundCommunityContribute.objects.all()
    fAgency = FundAgency.objects.all()
    total = []
    for ac in activity:
        fn,fm,fc,fa,total_fund =   [],[],[],[], []
        fn = FundNational.objects.filter(activity=ac.id).aggregate(Sum('national_amount'))
        fm = FundMunicipality.objects.filter(activity=ac.id).aggregate(Sum('municipality_amount'))
        fc = FundCommunityContribute.objects.filter(activity=ac.id).aggregate(Sum('communitycontribute_amount'))
        fa = FundAgency.objects.filter(activity=ac.id).aggregate(Sum('agency_amount'))
        if fn['national_amount__sum']:
            total_fund.append(fn['national_amount__sum'])
        if fm['municipality_amount__sum']:
            total_fund.append(fm['municipality_amount__sum'])
        if fc['communitycontribute_amount__sum']:
            total_fund.append(fc['communitycontribute_amount__sum'])
        if fa['agency_amount__sum']:
            total_fund.append(fa['agency_amount__sum'])
        total.append(np.sum(total_fund))
    df1 = pd.DataFrame(activity)
    df1['total_amount'] = total
    if municipality.name == 'Baucau' or municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera':   
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality} no Postu {post} iha Tinan {year}' 
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA no Postu {post} iha Tinan {year}' 
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality} no Postu {post} iha Tinan {year}' 
    data = {'title': title,
    'objects': df1, 
    'employee': employee,
    'page':"excelactivity",
    'fNational': fNational, 'fMunicipality': fMunicipality, 'fCommunity':fCommunity, 'fAgency':fAgency,
    'total_amount_national':total, 'municipality':municipality,'post':post,'year':year
            }
    return render(request, 'development/print/activity.html', data)

@login_required
def ReportActivity5(request, mun, post, village):
    empuser = None
    employee = None
    # EmployeeUser.objects.get(user = request.user).exists():
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    municipality = get_object_or_404(Municipality, id=mun)
    post = get_object_or_404(AdministrativePost, id=post)
    village = get_object_or_404(Village, id=village)
    activity = Activity.objects.filter(municipality=municipality, administrativepost=post, village=village)
    fNational = FundNational.objects.all()
    fMunicipality = FundMunicipality.objects.all()
    fCommunity = FundCommunityContribute.objects.all()
    fAgency = FundAgency.objects.all()
    total = []
    for ac in activity:
        fn,fm,fc,fa,total_fund =   [],[],[],[], []
        fn = FundNational.objects.filter(activity=ac.id).aggregate(Sum('national_amount'))
        fm = FundMunicipality.objects.filter(activity=ac.id).aggregate(Sum('municipality_amount'))
        fc = FundCommunityContribute.objects.filter(activity=ac.id).aggregate(Sum('communitycontribute_amount'))
        fa = FundAgency.objects.filter(activity=ac.id).aggregate(Sum('agency_amount'))
        if fn['national_amount__sum']:
            total_fund.append(fn['national_amount__sum'])
        if fm['municipality_amount__sum']:
            total_fund.append(fm['municipality_amount__sum'])
        if fc['communitycontribute_amount__sum']:
            total_fund.append(fc['communitycontribute_amount__sum'])
        if fa['agency_amount__sum']:
            total_fund.append(fa['agency_amount__sum'])
        total.append(np.sum(total_fund))
    df1 = pd.DataFrame(activity)
    df1['total_amount'] = total
    if municipality.name == 'Baucau' or municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera':   
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality}, Postu {post} no Suku {village}' 
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA, Postu {post} no Suku {village}' 
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality}, Postu {post} no Suku {village}' 
    data = {'title': title,
    'objects': df1, 
    'employee': employee,
    'page':"excelactivity",
    'fNational': fNational, 'fMunicipality': fMunicipality, 'fCommunity':fCommunity, 'fAgency':fAgency,
    'total_amount_national':total, 'municipality':municipality,'post':post,'village':village
            }
    return render(request, 'development/print/activity.html', data)

@login_required
def ReportActivity6(request, mun, post, village, year):
    empuser = None
    employee = None
    # EmployeeUser.objects.get(user = request.user).exists():
    try:
        empuser = EmployeeUser.objects.get(user = request.user)
        employee = Employee.objects.get(employeeuser=empuser)
    except:
        print('You are admin')
    municipality = get_object_or_404(Municipality, id=mun)
    post = get_object_or_404(AdministrativePost, id=post)
    village = get_object_or_404(Village, id=village)
    year = get_object_or_404(Year, year=year)
    activity = Activity.objects.filter(municipality=municipality, administrativepost=post, village=village, year=year)
    fNational = FundNational.objects.all()
    fMunicipality = FundMunicipality.objects.all()
    fCommunity = FundCommunityContribute.objects.all()
    fAgency = FundAgency.objects.all()
    total = []
    for ac in activity:
        fn,fm,fc,fa,total_fund =   [],[],[],[], []
        fn = FundNational.objects.filter(activity=ac.id).aggregate(Sum('national_amount'))
        fm = FundMunicipality.objects.filter(activity=ac.id).aggregate(Sum('municipality_amount'))
        fc = FundCommunityContribute.objects.filter(activity=ac.id).aggregate(Sum('communitycontribute_amount'))
        fa = FundAgency.objects.filter(activity=ac.id).aggregate(Sum('agency_amount'))
        if fn['national_amount__sum']:
            total_fund.append(fn['national_amount__sum'])
        if fm['municipality_amount__sum']:
            total_fund.append(fm['municipality_amount__sum'])
        if fc['communitycontribute_amount__sum']:
            total_fund.append(fc['communitycontribute_amount__sum'])
        if fa['agency_amount__sum']:
            total_fund.append(fa['agency_amount__sum'])
        total.append(np.sum(total_fund))
    df1 = pd.DataFrame(activity)
    df1['total_amount'] = total   
    if municipality.name == 'Baucau' or municipality.name == 'Dili' or municipality.name == 'Bobonaro' or municipality.name == 'Ermera':
        title = f'Relatóriu Dezenvolvimentu Autoridade Munisipal {municipality}, Postu {post} no Suku {village} iha Tinan {year}' 
    elif municipality.name == 'Oe-cusse':
        title = f'Relatóriu Dezenvolvimentu Rejiaun Autónomu RAEOA, Postu {post} no Suku {village} iha Tinan {year}' 
    else:
        title = f'Relatóriu Dezenvolvimentu Munisípiu {municipality}, Postu {post} no Suku {village} iha Tinan {year}' 
    data = {'title': title,
    'objects': df1, 
    'employee': employee,
    'page':"excelactivity",
    'fNational': fNational, 'fMunicipality': fMunicipality, 'fCommunity':fCommunity, 'fAgency':fAgency,
    'total_amount_national':total, 'municipality':municipality,'post':post,'village':village,'year':year
            }
    return render(request, 'development/print/activity.html', data)