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
def PrintProject7(request, year):
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
    'page':"printyear",
    'fVolunteer':fVolunteer, 
    'total_amount_national':total,'year':year,'activedevelopment':"active"}
    return render(request, 'development/print/project.html', data)

@login_required
def PrintProjectAll(request):
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
    title = f'Relatóriu Dezenvolvimentu Nasional'
    data = {
    'title': title, 
    'objects': df1, 
    'project':project,
    'employee': employee, 
    'fNational': fNational, 
    'fMunicipality': fMunicipality, 
    'fOng':fOng, 
    'page':"printyear",
    'fVolunteer':fVolunteer, 
    'total_amount_national':total,'activedevelopment':"active"}
    return render(request, 'development/print/project.html', data)

@login_required
def PrintProject1(request, mun):
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
        title = f'Relatóriu Dezenvolvimentu Munisipiu {municipality}'
    data = {
    'title': title, 
    'objects': df1, 
    'project':project,
    'employee': employee, 
    'fNational': fNational, 
    'fMunicipality': fMunicipality, 
    'fOng':fOng, 
    'fVolunteer':fVolunteer, 'activedevelopment':"active",
    'total_amount_national':total, 'municipality':municipality}
    return render(request, 'development/print/project.html', data)

@login_required
def PrintProject2(request, mun, year):
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
        title = f'Relatóriu Dezenvolvimentu Munisipiu {municipality} iha Tinan {year}'  
    data = {
    'title': title, 
    'objects': df1, 
    'project':project,
    # 'employee': employee, 
    'fNational': fNational, 
    'fMunicipality': fMunicipality, 
    'fOng':fOng, 
    'fVolunteer':fVolunteer, 'activedevelopment':"active",
    'total_amount_national':total, 'municipality':municipality,'year':year}
    return render(request, 'development/print/project.html', data)

@login_required
def PrintProject3(request, mun, post):
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
        title = f'Relatóriu Dezenvolvimentu Munisipiu {municipality} no Postu {post}'
    data = {
    'title': title, 
    'objects': df1, 
    'project':project,
    # 'employee': employee, 
    'fNational': fNational, 
    'fMunicipality': fMunicipality, 
    'fOng':fOng, 
    'fVolunteer':fVolunteer, 'activedevelopment':"active",
    'total_amount_national':total, 'municipality':municipality,'post':post}
    return render(request, 'development/print/project.html', data)

@login_required
def PrintProject4(request, mun, post, year):
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
        title = f'Relatóriu Dezenvolvimentu Munisipiu {municipality}, Postu {post} iha Tinan {year}'
    data = {
    'title': title, 
    'objects': df1, 
    'project':project,
    # 'employee': employee, 
    'fNational': fNational, 
    'fMunicipality': fMunicipality, 
    'fOng':fOng, 
    'fVolunteer':fVolunteer, 'activedevelopment':"active",
    'total_amount_national':total, 'municipality':municipality,'post':post,'year':year}
    return render(request, 'development/print/project.html', data)

@login_required
def PrintProject5(request, mun, post, village):
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
        title = f'Relatóriu Dezenvolvimentu Munisipiu {municipality}, Postu {post} no Suku {village}'
    data = {
    'title': title, 
    'objects': df1, 
    'project':project,
    # 'employee': employee, 
    'fNational': fNational, 
    'fMunicipality': fMunicipality, 
    'fOng':fOng, 
    'fVolunteer':fVolunteer, 'activedevelopment':"active",
    'total_amount_national':total, 'municipality':municipality,'post':post,'village':village}
    return render(request, 'development/print/project.html', data)

@login_required
def PrintProject6(request, mun, post, village, year):
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
        title = f'Relatóriu Dezenvolvimentu Munisipiu {municipality}, Postu {post} no Suku {village} iha Tinan {year}'
    data = {
    'title': title, 
    'objects': df1, 
    'project':project,
    # 'employee': employee, 
    'fNational': fNational, 
    'fMunicipality': fMunicipality, 
    'fOng':fOng, 
    'fVolunteer':fVolunteer, 
    'total_amount_national':total, 'municipality':municipality,'post':post,'village':village,
    'year':year,'activedevelopment':"active"}
    return render(request, 'development/print/project.html',data)


#Atividade 

@login_required
def PrintActivity1(request, mun):
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
        title = f'Relatóriu Dezenvolvimentu Munisipiu {municipality}' 
    data = {
    'title': title,'objects': df1,
    'fNational': fNational, 
    'fMunicipality': fMunicipality, 
    'fCommunity':fCommunity, 
    'fAgency':fAgency,
    'total_amount_national':total, 'municipality':municipality}
    return render(request, 'development/print/activity.html', data)

@login_required
def PrintActivityAll(request):
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
    'title': title,'objects': df1,
    'fNational': fNational, 
    'fMunicipality': fMunicipality, 
    'fCommunity':fCommunity, 
    'fAgency':fAgency,
    'total_amount_national':total}
    return render(request, 'development/print/activity.html', data)

@login_required
def PrintActivity7(request, year):
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
    # 'employee': employee,
    'fNational': fNational, 'fMunicipality': fMunicipality, 'fCommunity':fCommunity, 'fAgency':fAgency,
    'total_amount_national':total, 'year':year
            }
    return render(request, 'development/print/activity.html', data)

@login_required
def PrintActivity2(request, mun, year):
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
        title = f'Relatóriu Dezenvolvimentu Munisipiu {municipality} iha Tinan {year}' 
    data = {
    'title': title,
    'objects': df1, 
    # 'employee': employee,
    'fNational': fNational, 'fMunicipality': fMunicipality, 'fCommunity':fCommunity, 'fAgency':fAgency,
    'total_amount_national':total, 'municipality':municipality,'year':year
            }
    return render(request, 'development/print/activity.html',data)

@login_required
def PrintActivity3(request, mun, post):
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
        title = f'Relatóriu Dezenvolvimentu Munisipiu {municipality} no Postu {post}' 
    data = {'title': title,
    'objects': df1, 
    # 'employee': employee,
    'fNational': fNational, 'fMunicipality': fMunicipality, 'fCommunity':fCommunity, 'fAgency':fAgency,
    'total_amount_national':total, 'municipality':municipality,'post':post
            }
    return render(request, 'development/print/activity.html',data)

@login_required
def PrintActivity4(request, mun, post, year):
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
        title = f'Relatóriu Dezenvolvimentu Munisipiu {municipality} no Postu {post} iha Tinan {year}' 
    data = {'title': title,
    'objects': df1, 
    # 'employee': employee,
    'fNational': fNational, 'fMunicipality': fMunicipality, 'fCommunity':fCommunity, 'fAgency':fAgency,
    'total_amount_national':total, 'municipality':municipality,'post':post,'year':year
            }
    return render(request, 'development/print/activity.html',data)

@login_required
def PrintActivity5(request, mun, post, village):
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
        title = f'Relatóriu Dezenvolvimentu Munisipiu {municipality}, Postu {post} no Suku {village}' 
    data = {'title': title,
    'objects': df1, 
    # 'employee': employee,
    'fNational': fNational, 'fMunicipality': fMunicipality, 'fCommunity':fCommunity, 'fAgency':fAgency,
    'total_amount_national':total, 'municipality':municipality,'post':post,'village':village
            }
    return render(request, 'development/print/activity.html',data)

@login_required
def PrintActivity6(request, mun, post, village, year):
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
        title = f'Relatóriu Dezenvolvimentu Munisipiu {municipality}, Postu {post} no Suku {village} iha Tinan {year}' 
    data = {'title': title,
    'objects': df1, 
    # 'employee': employee,
    'fNational': fNational, 'fMunicipality': fMunicipality, 'fCommunity':fCommunity, 'fAgency':fAgency,
    'total_amount_national':total, 'municipality':municipality,'post':post,'village':village,'year':year
            }
    return render(request, 'development/print/activity.html',data)

