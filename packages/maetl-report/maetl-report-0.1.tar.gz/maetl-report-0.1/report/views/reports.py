from django.shortcuts import render, redirect, get_object_or_404
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
import numpy as np
from administration.models import Year
from main.decorators import allowed_users
from employee.models import *
from django.http import JsonResponse


def report_dashboard(request):
    context = {
        'title': 'Painel Relatoriu'
    }
    return render(request, 'report/dashboard.html', context)

def load_posts(request):
    # print('OKE')
    mun_id = request.GET.get('municipality')
    posts = AdministrativePost.objects.filter(municipality_id=mun_id).order_by('name')
    return render(request, 'custom/posts_dropdown.html', {'posts': posts})

def load_villages(request):
	post_id = request.GET.get('post')
	villages = Village.objects.filter(administrativepost_id=post_id).order_by('name')
	return render(request, 'custom/villages_dropdown.html', {'villages': villages})