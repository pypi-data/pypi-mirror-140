from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from custom.models import Municipality,AdministrativePost,Village,Aldeia
from population.models import Population,Deficient,DetailFamily,Family,Religion,Language,Profession,Citizen,User,Migration,Death,Migrationout,Level_Education
from population.utils import getnewidp,getnewidf
from population.forms import Family_form,Family_form,FamilyPosition,Population_form,DetailFamily_form,Death_form,Migration_form,Migrationout_form
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
from custom.utils import getnewid, getjustnewid, hash_md5, getlastid
from django.db.models import Count
from django.contrib import messages

import datetime
from django.db.models.functions import ExtractYear
from django.utils.dateparse import parse_date
from datetime import date
from django.shortcuts import get_object_or_404
from employee.models import *
from django.db.models import Q


from django.shortcuts import render,redirect
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.db.models import F





# iha dados kada munisipiu
@login_required
def reportb1jeralMunicipality(request):
    currentYear = date.today().year

    dataagora = timezone.now()

    tinan = date.today().year
    fulan = date.today().month
    year = date.today().year


    
    munisipiu_title = ""
    start_date = "2000-01-01"
    end_date = dataagora + timedelta(1)

    relijiaun = Religion.objects.all()
    edukasaun = Level_Education.objects.all()
    kondisaun = Deficient.objects.all()
    profession = Profession.objects.all()

    municipality = DetailFamily.objects.filter(Q(population__date_register__range=(start_date, end_date))  & Q(population__id_family = 'i') & Q(status = True) & Q(population__status_datap = 'ac')).values(municipality__name = F('family__municipality__name'), municipality__id = F('family__municipality__id')).annotate(count=Count('family__municipality__id')).order_by('family__municipality__id')
    totalpop = DetailFamily.objects.filter(Q(population__date_register__range=(start_date, end_date))  & Q(population__id_family = 'i') & Q(status = True) & Q(population__status_datap = 'ac')).values(municipality__name = F('family__municipality__name'), municipality__id = F('family__municipality__id')).count()
    kontafamilia = DetailFamily.objects.filter(Q(population__date_register__range=(start_date, end_date))  & Q(population__id_family = 'i') & Q(status = True)  & Q(population__status_datap = 'ac')).values('family__municipality__name','family__municipality__id').annotate(count=Count('family__id')).order_by('family__id')

    context = {
        'title': 'Populasaun Suku',
        'tinan' : currentYear,
        'title_tinan' : currentYear,
        'municipality' : municipality,
        'totalpop' : totalpop,
        'relijiaun' : relijiaun,
        'edukasaun' : edukasaun,
        'kondisaun' : kondisaun,
        'profession' : profession,
        'title' : 'Relatóriu Dadus Populasaun Iha Kada Munisípiu',  
        'kontafamilia' : len(kontafamilia),
    }
    return render(request, 'population_report/b1/reportjeral-b1.html',context)





@login_required
def popchar_munisipality(request):
    currentYear = date.today().year
    labels = []
    data = []

    munisipiu = Municipality.objects.all()

    dataagora = timezone.now()
    start_date = "2000-01-01"
    end_date = dataagora + timedelta(1)

    for entry in munisipiu: 
        konta = DetailFamily.objects.filter(Q(population__date_register__range=(start_date, end_date))  & Q(status = True) & Q(population__status_datap = 'ac') & Q(family__municipality__id = entry.id)).count()
        labels.append(entry.name)
        data.append(konta)


    return JsonResponse(data={
        'labels':labels,
        'data':data,
        })


@login_required
def popchar_familymunisipality(request):
    currentYear = date.today().year
    labels = []
    data = []

    dataagora = timezone.now()

    tinan = date.today().year
    fulan = date.today().month
    year = date.today().year


    munisipiu_title = ""
    start_date = "2000-01-01"
    end_date = dataagora + timedelta(1)

    munisipiu = Municipality.objects.all()

    for entry in munisipiu: 
        konta = DetailFamily.objects.filter(Q(population__date_register__range=(start_date, end_date)) & Q(status = True)  & Q(family__municipality__id = entry.id) & Q(population__status_datap = 'ac')).values('family__municipality__name','family__municipality__id').annotate(count=Count('family__id')).order_by('family__id')

        labels.append(entry.name)
        data.append(len(konta))
        
    return JsonResponse(data={
        'labels':labels,
        'data':data,
        })








@login_required
def reportb1_printjeral(request):


    gender=""
    citizenp = ""
    religion = ""
    level_education = ""
    kondisaun = ""
    vurneravel = ""
    vurdata = ""
    titulu_kategoria = ""
    marital_status = ""
    profession = ""



    if request.GET['kondisaun'] != "jeral" :
        kondisaun = "& Q(population__deficient = request.GET['kondisaun'])"
        naran_kond = Deficient.objects.get(id=request.GET['kondisaun'])
        titulu_kategoria = titulu_kategoria + " (Kondisaun Fiziku :"+ naran_kond.name +" )" 


    if request.GET['vurneravel'] != "jeral" :
        if request.GET['vurneravel'] == 'True' :
            vurneravel = "& Q(population__vulnerable = True )"

        elif request.GET['vurneravel'] == 'False' :
            vurneravel = "& Q(population__vulnerable = False )"
            titulu_kategoria = titulu_kategoria + " ( Populasaun : Vurneralvel)"



    if request.GET['gender'] != "jeral" :
        gender = " & Q(population__gender = request.GET['gender'])"
        titulu_kategoria = titulu_kategoria + " ( Sexu : " + request.GET['gender'] + ")"
  

    if request.GET['citizenp'] != "jeral" :
        citizenp = " & Q(population__citizenp = request.GET['citizenp'])"
        if request.GET['citizenp'] == 'a' :
            titulu_kategoria = titulu_kategoria + " (Sidadaun : Adkeridu)"
        elif request.GET['citizenp'] == 'o' :
            titulu_kategoria = titulu_kategoria + " (Sidadaun : Orijinal)"
    
    if request.GET['religion'] != "jeral" :
        religion = " & Q(population__religion = request.GET['religion'])"
        naran_relig = Religion.objects.get(id=request.GET['religion'])
        titulu_kategoria = titulu_kategoria + " (Relijiaun :"+ naran_relig.name +" )" 

    if request.GET['level_education'] != "jeral" :
        level_education = " & Q(population__level_education = request.GET['level_education'])"
        naran_edu = Level_Education.objects.get(id=request.GET['level_education'])
        titulu_kategoria = titulu_kategoria + " (Habilitasaun Literariu :"+ naran_edu.name +" )" 


    if request.GET['profession'] != "jeral" :
        profession = " & Q(population__profession = request.GET['profession'])"
        naran_prof = Profession.objects.get(id=request.GET['profession'])
        titulu_kategoria = titulu_kategoria + " (Profisaun :"+ naran_prof.name +" )" 



    if request.GET['marital_status'] != "jeral" :

        marital_code = request.GET['marital_status']
        marital_status = " & Q(population__marital_status = request.GET['marital_status'])"

        if marital_code == "s" :
            titulu_kategoria = titulu_kategoria + " (Estadu Civil : Klosan )" 
        elif marital_code == "c" :
            titulu_kategoria = titulu_kategoria + " (Estadu Civil : Kaben Nain )" 
        elif marital_code == "d" :
            titulu_kategoria = titulu_kategoria + " (Estadu Civil : Fahe Malu )" 
        elif marital_code == "f" :
            titulu_kategoria = titulu_kategoria + " (Estadu Civil : Faluk )" 





    dataagora = timezone.now()
    tinan = date.today().year
    fulan = date.today().month
    year = date.today().year

    munisipiu_title = ""
    start_date = "2000-01-01"
    end_date = dataagora + timedelta(1)



    family_member = []
    querrysetstring = "DetailFamily.objects.filter(Q(population__date_register__range=(start_date, end_date))  & Q(population__status_datap = 'ac') & Q(population__id_family = 'i') & Q(status = True) "+ gender + citizenp + religion + level_education  +  vurneravel  + kondisaun  + profession + marital_status +  ").order_by('family__municipality')"
    familymember_list = eval(querrysetstring)
    count = 0
    for dados in familymember_list.iterator():
            count = count + 1

            linguadata = ""
            datalingua = ""


            if dados.population.language != None :
                datalingua = dados.population.language
                datalingua = datalingua.split('-')
            else : 
                linguadata = "Dadus Laiha"
          
            lingualop = []
            language = Language.objects.all()
            
            for dadoslingua in language : 
                if str(dadoslingua.id) in datalingua :
                    linguadata = linguadata + "- " + dadoslingua.name + "  " 
        
            family_member.append({
                'family' : dados.family.id_family,
                'family_position' : dados.family_position,
                'id': dados.population.id,
                'hashed' : dados.hashed,
                'village': dados.population.village, 
                'aldeia':  str(dados.population.aldeia) +" / "+ str(dados.population.aldeia.village) +" / "+  str(dados.population.aldeia.village.administrativepost) +" / "+  str(dados.population.aldeia.village.administrativepost.municipality) , 
                'profession': dados.population.profession,
                'citizenp': dados.population.citizenp,
                'religion': dados.population.religion, 
                'user_created': dados.population.user_created,
                'name': dados.population.name,
                'date_of_bird': dados.population.date_of_bird, 
                'place_of_bird': dados.population.place_of_bird,
                'gender': dados.population.gender,
                'marital_status': dados.population.marital_status,
                'level_education': dados.population.level_education, 
                'readalatin': dados.population.readalatin, 
                'readaarabe': dados.population.readaarabe,
                'readachina': dados.population.readachina,
                'nu_bi': dados.population.nu_bi,
                'id_family': dados.family,
                'descriptionp': dados.population.descriptionp,
                'imagen': dados.population.imagen, 
                'status_datap': dados.population.status_datap,
                'type_data': dados.population.type_data,
                'date_created': dados.population.date_created,

                'lingua': linguadata,
                'nu_e': dados.population.nu_e,
                'nu_p': dados.population.nu_p,
                'kondisaun': dados.population.deficient,
                'phone': dados.population.phone,
                'vulnerable': dados.population.vulnerable,
                })
    context = {
        'title': 'Populasaun Suku',
        'family_member' : family_member,
        'title' : 'Relatóriu Dadus Populasaun suku',
        'dataagora' : dataagora,
        'totpop' : len(family_member),
        'munisipiu' : 'Jeral',
        'postu' : 'mamuk',
        'titulu_kategoria' : titulu_kategoria,
        'suku' : 'mamuk'
    }
    return render(request, 'population_report/b1/reportjeral-b1-print.html', context)


































#klik tama iha munisipiu tama ba postu
@login_required
def reportb1jeralPostadministrative(request,id):
    currentYear = date.today().year
    dataagora = timezone.now()

    tinan = date.today().year
    fulan = date.today().month
    year = date.today().year

    
    start_date = "2000-01-01"
    end_date = dataagora + timedelta(1)

    munisipiu_title = ""
    munisipiu = Municipality.objects.get(id=id)

    relijiaun = Religion.objects.all()
    edukasaun = Level_Education.objects.all()
    kondisaun = Deficient.objects.all()
    profession = Profession.objects.all()


    postu = DetailFamily.objects.filter(Q(family__municipality= id) & Q(status = True) & Q(population__date_register__range=(start_date, end_date))  & Q(population__id_family = 'i') & Q(population__status_datap = 'ac')).values(administrativepost__name = F('family__administrativepost__name'), administrativepost__id =  F('family__administrativepost__id')).annotate(count=Count('population__id')).order_by('family__administrativepost__id')
    totalpop = DetailFamily.objects.filter(Q(family__municipality= id) & Q(status = True) & Q(population__date_register__range=(start_date, end_date))  & Q(population__id_family = 'i') & Q(population__status_datap = 'ac')).count()

    kontafamilia = DetailFamily.objects.filter(Q(population__date_register__range=(start_date, end_date)) & Q(status = True) & Q(population__id_family = 'i') & Q(family__municipality__id= id) & Q(population__status_datap = 'ac')).values('family__municipality__name','family__municipality__id').annotate(count=Count('family__id')).order_by('family__id')
    context = {
        'title': 'Populasaun Suku',
        'postu' : postu,
        'id' : id,

        'relijiaun' : relijiaun,
        'profession' : profession,
        'edukasaun' : edukasaun,
        'kondisaun' : kondisaun,
        'kontafamilia': len(kontafamilia),
        'totalpop' : totalpop,
        'munisipiu' : munisipiu.name,
        'title' : 'Relatóriu Dadus Populasaun iha Kada Postu Administrativu' ,  
    }
    return render(request, 'population_report/b1/reportjeral-b1-administrative.html',context)


    


def popchar_postadministrative(request,id):

    currentYear = date.today().year
    labels = []
    data = []
    dataagora = timezone.now()

    tinan = date.today().year
    fulan = date.today().month
    year = date.today().year


    munisipiu_title = ""
    start_date = "2000-01-01"
    end_date = dataagora + timedelta(1)

  
    postu = AdministrativePost.objects.filter(municipality__id = id)
    for entry in postu: 
        konta = DetailFamily.objects.filter(Q(population__date_register__range=(start_date, end_date)) & Q(status = True)  & Q(population__id_family = 'i') & Q(population__status_datap = 'ac') & Q(family__administrativepost__id = entry.id)).count()
        labels.append(entry.name)
        data.append(konta)
    return JsonResponse(data={
        'labels':labels,
        'data':data,
        })


@login_required
def popchar_familypostadministrative(request,id):
    currentYear = date.today().year
    labels = []
    data = []

    dataagora = timezone.now()

    tinan = date.today().year
    fulan = date.today().month
    year = date.today().year


    munisipiu_title = ""
    start_date = "2000-01-01"
    end_date = dataagora + timedelta(1)

    postu = AdministrativePost.objects.filter(municipality__id = id)
    for entry in postu: 
        konta = DetailFamily.objects.filter(Q(population__date_register__range=(start_date, end_date)) & Q(status = True)  & Q(population__id_family = 'i') & Q(family__administrativepost__id = entry.id) & Q(population__status_datap = 'ac')).values('family__municipality__name','family__municipality__id').annotate(count=Count('family__id')).order_by('family__id')

        labels.append(entry.name)
        data.append(len(konta))
        
    return JsonResponse(data={
        'labels':labels,
        'data':data,
        })






@login_required
def reportb1_printPostadministrative(request,id):






    gender=""
    citizenp = ""
    religion = ""
    level_education = ""
    kondisaun = ""
    vurneravel = ""
    vurdata = ""
    titulu_kategoria = ""
    marital_status = ""
    profession = ""



    if request.GET['kondisaun'] != "jeral" :
        kondisaun = "& Q(population__deficient = request.GET['kondisaun'])"
        naran_kond = Deficient.objects.get(id=request.GET['kondisaun'])
        titulu_kategoria = titulu_kategoria + " (Kondisaun Fiziku :"+ naran_kond.name +" )" 


    if request.GET['vurneravel'] != "jeral" :
        if request.GET['vurneravel'] == 'True' :
            vurneravel = "& Q(population__vulnerable = True )"

        elif request.GET['vurneravel'] == 'False' :
            vurneravel = "& Q(population__vulnerable = False )"
            titulu_kategoria = titulu_kategoria + " ( Populasaun : Vurneralvel)"



    if request.GET['gender'] != "jeral" :
        gender = " & Q(population__gender = request.GET['gender'])"
        titulu_kategoria = titulu_kategoria + " ( Sexu : " + request.GET['gender'] + ")"
  

    if request.GET['citizenp'] != "jeral" :
        citizenp = " & Q(population__citizenp = request.GET['citizenp'])"
        if request.GET['citizenp'] == 'a' :
            titulu_kategoria = titulu_kategoria + " (Sidadaun : Adkeridu)"
        elif request.GET['citizenp'] == 'o' :
            titulu_kategoria = titulu_kategoria + " (Sidadaun : Orijinal)"
    
    if request.GET['religion'] != "jeral" :
        religion = " & Q(population__religion = request.GET['religion'])"
        naran_relig = Religion.objects.get(id=request.GET['religion'])
        titulu_kategoria = titulu_kategoria + " (Relijiaun :"+ naran_relig.name +" )" 

    if request.GET['level_education'] != "jeral" :
        level_education = " & Q(population__level_education = request.GET['level_education'])"
        naran_edu = Level_Education.objects.get(id=request.GET['level_education'])
        titulu_kategoria = titulu_kategoria + " (Habilitasaun Literariu :"+ naran_edu.name +" )" 


    if request.GET['profession'] != "jeral" :
        profession = " & Q(population__profession = request.GET['profession'])"
        naran_prof = Profession.objects.get(id=request.GET['profession'])
        titulu_kategoria = titulu_kategoria + " (Profisaun :"+ naran_prof.name +" )" 



    if request.GET['marital_status'] != "jeral" :

        marital_code = request.GET['marital_status']
        marital_status = " & Q(population__marital_status = request.GET['marital_status'])"

        if marital_code == "s" :
            titulu_kategoria = titulu_kategoria + " (Estadu Civil : Klosan )" 
        elif marital_code == "c" :
            titulu_kategoria = titulu_kategoria + " (Estadu Civil : Kaben Nain )" 
        elif marital_code == "d" :
            titulu_kategoria = titulu_kategoria + " (Estadu Civil : Fahe Malu )" 
        elif marital_code == "f" :
            titulu_kategoria = titulu_kategoria + " (Estadu Civil : Faluk )" 



    family_member = []

    tinan = date.today().year
    fulan = date.today().month
    year = date.today().year

    munisipiu = Municipality.objects.get(id=id)

    dataagora = timezone.now()    
    start_date = "2000-01-01"
    end_date = dataagora + timedelta(1)


    querrysetstring  = "DetailFamily.objects.filter(Q(population__date_register__range=(start_date, end_date))  & Q(population__status_datap = 'ac') & Q(population__id_family = 'i') & Q(status = True) & Q(family__municipality__id = id) "+ gender + citizenp + religion + level_education  +  vurneravel  + kondisaun  + profession + marital_status + ").order_by('family__municipality')"
    familymember_list = eval(querrysetstring)

    count = 0
    for dados in familymember_list.iterator():
            count = count + 1

            linguadata = ""
            datalingua = ""


            if dados.population.language != None :
                datalingua = dados.population.language
                datalingua = datalingua.split('-')
            else : 
                linguadata = "Dadus Laiha"
          
            lingualop = []
            language = Language.objects.all()
            
            for dadoslingua in language : 
                if str(dadoslingua.id) in datalingua :
                    linguadata = linguadata + "- " + dadoslingua.name + "  " 
        
            family_member.append({
                'family' : dados.family.id_family,
                'family_position' : dados.family_position,
                'id': dados.population.id,
                'hashed' : dados.hashed,
                'village': dados.population.village, 
                'aldeia':  str(dados.population.aldeia) +" / "+ str(dados.population.aldeia.village) +" / "+  str(dados.population.aldeia.village.administrativepost) +" / "+  str(dados.population.aldeia.village.administrativepost.municipality) , 
                'profession': dados.population.profession,
                'citizenp': dados.population.citizenp,
                'religion': dados.population.religion, 
                'user_created': dados.population.user_created,
                'name': dados.population.name,
                'date_of_bird': dados.population.date_of_bird, 
                'place_of_bird': dados.population.place_of_bird,
                'gender': dados.population.gender,
                'marital_status': dados.population.marital_status,
                'level_education': dados.population.level_education, 
                'readalatin': dados.population.readalatin, 
                'readaarabe': dados.population.readaarabe,
                'readachina': dados.population.readachina,
                'nu_bi': dados.population.nu_bi,
                'id_family': dados.family,
                'descriptionp': dados.population.descriptionp,
                'imagen': dados.population.imagen, 
                'status_datap': dados.population.status_datap,
                'type_data': dados.population.type_data,
                'date_created': dados.population.date_created,

                'lingua': linguadata,
                'nu_e': dados.population.nu_e,
                'nu_p': dados.population.nu_p,
                'kondisaun': dados.population.deficient,
                'phone': dados.population.phone,
                'vulnerable': dados.population.vulnerable,


                })
    context = {
        'title': 'Populasaun Suku',
        'family_member' : family_member,
        'title' : 'Relatóriu Dadus Populasaun suku',
        'munisipiu' : munisipiu.name,
        'totpop' : len(family_member),
        'postu' : 'mamuk',
        'suku' : 'mamuk',
        'totpop' : len(family_member),
        'titulu_kategoria' : titulu_kategoria,
        'tinan' : tinan
        
    }
    return render(request, 'population_report/b1/reportjeral-b1-print.html', context)


































#klik iha postu tama ba suku

@login_required
def reportb1jeralVillage(request,id):
    currentYear = date.today().year

    dataagora = timezone.now()

    tinan = date.today().year
    fulan = date.today().month
    year = date.today().year

    munisipiu_title = ""
    start_date = "2000-01-01"
    end_date = dataagora + timedelta(1)


    relijiaun = Religion.objects.all()
    edukasaun = Level_Education.objects.all()
    kondisaun = Deficient.objects.all()
    profession = Profession.objects.all()


    postu = AdministrativePost.objects.get(id=id)
    suku = DetailFamily.objects.filter(Q(family__administrativepost= id)  & Q(population__date_register__range=(start_date, end_date))  & Q(population__id_family = 'i') & Q(status=True) & Q(population__status_datap = 'ac')).values(village__name = F('family__village__name'), village__id =  F('family__village__id')).annotate(count=Count('family__village__id')).order_by('family__village__id')

    totalpop = DetailFamily.objects.filter(Q(family__administrativepost= id)  & Q(population__date_register__range=(start_date, end_date))  & Q(status=True) & Q(population__id_family = 'i') & Q(population__status_datap = 'ac')).count()

    kontafamilia = DetailFamily.objects.filter(Q(population__date_register__range=(start_date, end_date))   & Q(status=True) & Q(population__id_family = 'i') & Q(family__administrativepost__id = id) & Q(population__status_datap = 'ac')).values('family__municipality__name','family__municipality__id').annotate(count=Count('family__id')).order_by('family__id')

    context = {
        'title': 'Populasaun Suku',
        'suku' : suku,
        'id' : id,
        'totalpop' : totalpop,
        'postu' : postu.name,
        'relijiaun' : relijiaun,
        'edukasaun' : edukasaun,
        'profession' : profession,
        'kondisaun' : kondisaun,
        'kontafamilia' : len(kontafamilia),
        'id_munisipiu' : postu.municipality.id,
        'munisipiu' : postu.municipality.name,
        'title' : 'Relatóriu Dadus Populasaun iha kada suku ',  
    }
    return render(request, 'population_report/b1/reportjeral-b1-village.html',context)






def popchar_village(request,id):

    currentYear = date.today().year

    dataagora = timezone.now()

    tinan = date.today().year
    fulan = date.today().month
    year = date.today().year


    munisipiu_title = ""
    start_date = "2000-01-01"
    end_date = dataagora + timedelta(1)


    labels = []
    data = []
    
    suku = Village.objects.filter(administrativepost__id = id)
    for entry in suku: 
        konta = DetailFamily.objects.filter(Q(population__date_register__range=(start_date, end_date)) & Q(status=True)  & Q(population__id_family = 'i') & Q(population__status_datap = 'ac') & Q(family__village__id = entry.id)).count()
        labels.append(entry.name)
        data.append(konta)
    return JsonResponse(data={
        'labels':labels,
        'data':data,
        })


@login_required
def popchar_familyvillage(request,id):
    currentYear = date.today().year
    labels = []
    data = []

    dataagora = timezone.now()

    tinan = date.today().year
    fulan = date.today().month
    year = date.today().year


    munisipiu_title = ""
    start_date = "2000-01-01"
    end_date = dataagora + timedelta(1)

    suku = Village.objects.filter(administrativepost__id = id)
    for entry in suku: 
        konta = DetailFamily.objects.filter(Q(population__date_register__range=(start_date, end_date)) & Q(status=True) & Q(population__id_family = 'i') & Q(family__village__id = entry.id) & Q(population__status_datap = 'ac')).values('family__municipality__name','family__municipality__id').annotate(count=Count('family__id')).order_by('family__id')

        labels.append(entry.name)
        data.append(len(konta))
        
    return JsonResponse(data={
        'labels':labels,
        'data':data,
        })
        



@login_required
def reportb1_printVillage(request,id):


    gender=""
    citizenp = ""
    religion = ""
    level_education = ""
    kondisaun = ""
    vurneravel = ""
    vurdata = ""
    titulu_kategoria = ""
    marital_status = ""
    profession = ""



    if request.GET['kondisaun'] != "jeral" :
        kondisaun = "& Q(population__deficient = request.GET['kondisaun'])"
        naran_kond = Deficient.objects.get(id=request.GET['kondisaun'])
        titulu_kategoria = titulu_kategoria + " (Kondisaun Fiziku :"+ naran_kond.name +" )" 


    if request.GET['vurneravel'] != "jeral" :
        if request.GET['vurneravel'] == 'True' :
            vurneravel = "& Q(population__vulnerable = True )"

        elif request.GET['vurneravel'] == 'False' :
            vurneravel = "& Q(population__vulnerable = False )"
            titulu_kategoria = titulu_kategoria + " ( Populasaun : Vurneralvel)"



    if request.GET['gender'] != "jeral" :
        gender = " & Q(population__gender = request.GET['gender'])"
        titulu_kategoria = titulu_kategoria + " ( Sexu : " + request.GET['gender'] + ")"
  

    if request.GET['citizenp'] != "jeral" :
        citizenp = " & Q(population__citizenp = request.GET['citizenp'])"
        if request.GET['citizenp'] == 'a' :
            titulu_kategoria = titulu_kategoria + " (Sidadaun : Adkeridu)"
        elif request.GET['citizenp'] == 'o' :
            titulu_kategoria = titulu_kategoria + " (Sidadaun : Orijinal)"
    
    if request.GET['religion'] != "jeral" :
        religion = " & Q(population__religion = request.GET['religion'])"
        naran_relig = Religion.objects.get(id=request.GET['religion'])
        titulu_kategoria = titulu_kategoria + " (Relijiaun :"+ naran_relig.name +" )" 

    if request.GET['level_education'] != "jeral" :
        level_education = " & Q(population__level_education = request.GET['level_education'])"
        naran_edu = Level_Education.objects.get(id=request.GET['level_education'])
        titulu_kategoria = titulu_kategoria + " (Habilitasaun Literariu :"+ naran_edu.name +" )" 


    if request.GET['profession'] != "jeral" :
        profession = " & Q(population__profession = request.GET['profession'])"
        naran_prof = Profession.objects.get(id=request.GET['profession'])
        titulu_kategoria = titulu_kategoria + " (Profisaun :"+ naran_prof.name +" )" 



    if request.GET['marital_status'] != "jeral" :

        marital_code = request.GET['marital_status']
        marital_status = " & Q(population__marital_status = request.GET['marital_status'])"

        if marital_code == "s" :
            titulu_kategoria = titulu_kategoria + " (Estadu Civil : Klosan )" 
        elif marital_code == "c" :
            titulu_kategoria = titulu_kategoria + " (Estadu Civil : Kaben Nain )" 
        elif marital_code == "d" :
            titulu_kategoria = titulu_kategoria + " (Estadu Civil : Fahe Malu )" 
        elif marital_code == "f" :
            titulu_kategoria = titulu_kategoria + " (Estadu Civil : Faluk )" 



    tinan = date.today().year
    postu = AdministrativePost.objects.get(id=id)   

    dataagora = timezone.now()    
    start_date = "2000-01-01"
    end_date = dataagora + timedelta(1)


    family_member = []
    querrysetstring  = "DetailFamily.objects.filter(Q(population__date_register__range=(start_date, end_date))  & Q(population__status_datap = 'ac') & Q(population__id_family = 'i') & Q(status = True) & Q(family__administrativepost__id = id) "+ gender + citizenp + religion + level_education  +  vurneravel  + kondisaun + profession + marital_status +  ").order_by('family__administrativepost')"
    familymember_list = eval(querrysetstring) 
    count = 0
    for dados in familymember_list.iterator():
            count = count + 1

            linguadata = ""
            datalingua = ""


            if dados.population.language != None :
                datalingua = dados.population.language
                datalingua = datalingua.split('-')
            else : 
                linguadata = "Dadus Laiha"
          
            lingualop = []
            language = Language.objects.all()
            
            for dadoslingua in language : 
                if str(dadoslingua.id) in datalingua :
                    linguadata = linguadata + "- " + dadoslingua.name + "  " 
        
            family_member.append({
                'family' : dados.family.id_family,
                'family_position' : dados.family_position,
                'id': dados.population.id,
                'hashed' : dados.hashed,
                'village': dados.population.village, 
                'aldeia':  str(dados.population.aldeia) +" / "+ str(dados.population.aldeia.village) +" / "+  str(dados.population.aldeia.village.administrativepost) +" / "+  str(dados.population.aldeia.village.administrativepost.municipality) , 
                'profession': dados.population.profession,
                'citizenp': dados.population.citizenp,
                'religion': dados.population.religion, 
                'user_created': dados.population.user_created,
                'name': dados.population.name,
                'date_of_bird': dados.population.date_of_bird, 
                'place_of_bird': dados.population.place_of_bird,
                'gender': dados.population.gender,
                'marital_status': dados.population.marital_status,
                'level_education': dados.population.level_education, 
                'readalatin': dados.population.readalatin, 
                'readaarabe': dados.population.readaarabe,
                'readachina': dados.population.readachina,
                'nu_bi': dados.population.nu_bi,
                'id_family': dados.family,
                'descriptionp': dados.population.descriptionp,
                'imagen': dados.population.imagen, 
                'status_datap': dados.population.status_datap,
                'type_data': dados.population.type_data,
                'date_created': dados.population.date_created,

                'lingua': linguadata,
                'nu_e': dados.population.nu_e,
                'nu_p': dados.population.nu_p,
                'kondisaun': dados.population.deficient,
                'phone': dados.population.phone,
                'vulnerable': dados.population.vulnerable,


                })
    context = {
        'title': 'Populasaun Suku',
        'family_member' : family_member,
        'title' : 'Relatoriu Dadus Populasaun suku',
        'suku' : 'mamuk',
        'totpop' : len(family_member),
        'postu' : postu.name,
        'titulu_kategoria' : titulu_kategoria,
        'munisipiu' : postu.municipality.name,
        'tinan' : tinan
        
    }
    return render(request, 'population_report/b1/reportjeral-b1-print.html', context)





































@login_required
def reportb1jeralAldeia(request,id):
    currentYear = date.today().year
    dataagora = timezone.now()
    suku = Village.objects.get(id=id)


    tinan = date.today().year
    fulan = date.today().month
    year = date.today().year

    relijiaun = Religion.objects.all()
    edukasaun = Level_Education.objects.all()
    kondisaun = Deficient.objects.all()
    profession = Profession.objects.all()

    munisipiu_title = ""
    start_date = "2000-01-01"
    end_date = dataagora + timedelta(1)


    aldeia = DetailFamily.objects.filter(Q(family__village = id)  & Q(population__date_register__range=(start_date, end_date))  & Q(status = True)  & Q(population__status_datap = 'ac')).values( aldeia__name =  F('family__aldeia__name'), aldeia__id =  F('family__aldeia__id')).annotate(count=Count('family__aldeia__id')).order_by('family__aldeia__id')
    
    totalpop = DetailFamily.objects.filter(Q(family__village = id)  & Q(population__date_register__range=(start_date, end_date)) & Q(status = True)   & Q(population__status_datap = 'ac')).count()

    kontafamilia = DetailFamily.objects.filter(Q(population__date_register__range=(start_date, end_date))  & Q(population__id_family = 'i') & Q(family__village__id = id) & Q(population__status_datap = 'ac')).values('family__municipality__name','family__municipality__id').annotate(count=Count('family__id')).order_by('family__id')


    context = {
        'title': 'Populasaun Suku',
        'aldeia' : aldeia,
        'id' : id,
        'suku' : suku.name,
        'kontafamilia' : len(kontafamilia),
        'totalpop' : totalpop,
        'relijiaun' : relijiaun,
        'edukasaun' : edukasaun,
        'profession' : profession,
        'kondisaun' : kondisaun,
        'id_postu' : suku.administrativepost.id,
        'postu' : suku.administrativepost.name,
        'munisipiu' : suku.administrativepost.municipality.name,
        'title' : 'Relatóriu Dadus Populasaun iha kada aldeia',  
    }
    return render(request, 'population_report/b1/reportjeral-b1-aldeia.html',context)





@login_required
def reportb1_printAldeia(request,id): 



    gender=""
    citizenp = ""
    religion = ""
    level_education = ""
    kondisaun = ""
    vurneravel = ""
    vurdata = ""
    marital_status = ""
    profession = ""

    titulu_kategoria = ""



    if request.GET['kondisaun'] != "jeral" :
        kondisaun = "& Q(population__deficient = request.GET['kondisaun'])"
        naran_kond = Deficient.objects.get(id=request.GET['kondisaun'])
        titulu_kategoria = titulu_kategoria + " (Kondisaun Fiziku :"+ naran_kond.name +" )" 


    if request.GET['vurneravel'] != "jeral" :
        if request.GET['vurneravel'] == 'True' :
            vurneravel = "& Q(population__vulnerable = True )"

        elif request.GET['vurneravel'] == 'False' :
            vurneravel = "& Q(population__vulnerable = False )"
            titulu_kategoria = titulu_kategoria + " ( Populasaun : Vurneralvel)"



    if request.GET['gender'] != "jeral" :
        gender = " & Q(population__gender = request.GET['gender'])"
        titulu_kategoria = titulu_kategoria + " ( Sexu : " + request.GET['gender'] + ")"
  

    if request.GET['citizenp'] != "jeral" :
        citizenp = " & Q(population__citizenp = request.GET['citizenp'])"
        if request.GET['citizenp'] == 'a' :
            titulu_kategoria = titulu_kategoria + " (Sidadaun : Adkeridu)"
        elif request.GET['citizenp'] == 'o' :
            titulu_kategoria = titulu_kategoria + " (Sidadaun : Orijinal)"
    
    if request.GET['religion'] != "jeral" :
        religion = " & Q(population__religion = request.GET['religion'])"
        naran_relig = Religion.objects.get(id=request.GET['religion'])
        titulu_kategoria = titulu_kategoria + " (Relijiaun :"+ naran_relig.name +" )" 

    if request.GET['level_education'] != "jeral" :
        level_education = " & Q(population__level_education = request.GET['level_education'])"
        naran_edu = Level_Education.objects.get(id=request.GET['level_education'])
        titulu_kategoria = titulu_kategoria + " (Habilitasaun Literariu :"+ naran_edu.name +" )" 


    if request.GET['profession'] != "jeral" :
        profession = " & Q(population__profession = request.GET['profession'])"
        naran_prof = Profession.objects.get(id=request.GET['profession'])
        titulu_kategoria = titulu_kategoria + " (Profisaun :"+ naran_prof.name +" )" 



    if request.GET['marital_status'] != "jeral" :

        marital_code = request.GET['marital_status']
        marital_status = " & Q(population__marital_status = request.GET['marital_status'])"

        if marital_code == "s" :
            titulu_kategoria = titulu_kategoria + " (Estadu Civil : Klosan )" 
        elif marital_code == "c" :
            titulu_kategoria = titulu_kategoria + " (Estadu Civil : Kaben Nain )" 
        elif marital_code == "d" :
            titulu_kategoria = titulu_kategoria + " (Estadu Civil : Fahe Malu )" 
        elif marital_code == "f" :
            titulu_kategoria = titulu_kategoria + " (Estadu Civil : Faluk )" 


    tinan = date.today().year
    suku = Village.objects.get(id=id)   


    dataagora = timezone.now()    
    start_date = "2000-01-01"
    end_date = dataagora + timedelta(1)


    family_member = []
    querrysetstring  = "DetailFamily.objects.filter(Q(population__date_register__range=(start_date, end_date))  & Q(population__status_datap = 'ac') & Q(population__id_family = 'i') & Q(status = True) & Q(family__village__id = id) "+ gender + citizenp + religion + level_education  +  vurneravel  + kondisaun  + profession + marital_status + " ).order_by('family__village')"
    familymember_list = eval(querrysetstring)
    count = 0
    for dados in familymember_list.iterator():
            count = count + 1

            linguadata = ""
            datalingua = ""


            if dados.population.language != None :
                datalingua = dados.population.language
                datalingua = datalingua.split('-')
            else : 
                linguadata = "Dadus Laiha"
          
            lingualop = []
            language = Language.objects.all()
            
            for dadoslingua in language : 
                if str(dadoslingua.id) in datalingua :
                    linguadata = linguadata + "- " + dadoslingua.name + "  " 
        
            family_member.append({
                'family' : dados.family.id_family,
                'family_position' : dados.family_position,
                'id': dados.population.id,
                'hashed' : dados.hashed,
                'village': dados.population.village, 
                'aldeia':  str(dados.population.aldeia) +" / "+ str(dados.population.aldeia.village) +" / "+  str(dados.population.aldeia.village.administrativepost) +" / "+  str(dados.population.aldeia.village.administrativepost.municipality) , 
                'profession': dados.population.profession,
                'citizenp': dados.population.citizenp,
                'religion': dados.population.religion, 
                'user_created': dados.population.user_created,
                'name': dados.population.name,
                'date_of_bird': dados.population.date_of_bird, 
                'place_of_bird': dados.population.place_of_bird,
                'gender': dados.population.gender,
                'marital_status': dados.population.marital_status,
                'level_education': dados.population.level_education, 
                'readalatin': dados.population.readalatin, 
                'readaarabe': dados.population.readaarabe,
                'readachina': dados.population.readachina,
                'nu_bi': dados.population.nu_bi,
                'id_family': dados.family,
                'descriptionp': dados.population.descriptionp,
                'imagen': dados.population.imagen, 
                'status_datap': dados.population.status_datap,
                'type_data': dados.population.type_data,
                'date_created': dados.population.date_created,

                'lingua': linguadata,
                'nu_e': dados.population.nu_e,
                'nu_p': dados.population.nu_p,
                'kondisaun': dados.population.deficient,
                'phone': dados.population.phone,
                'vulnerable': dados.population.vulnerable,


                })
    context = {
        'title': 'Populasaun Suku',
        'family_member' : family_member,
        'title' : 'Relatorio Dadus Populasaun suku',
        'titulu_kategoria' : titulu_kategoria,
        'suku' : suku.name,
        'totpop' : len(family_member),
        'postu' : suku.administrativepost.name,
        'munisipiu' : suku.administrativepost.municipality.name,
        'tinan' : tinan
        
    }
    return render(request, 'population_report/b1/reportjeral-b1-print.html', context)







def popchar_aldeia(request,id):

    dataagora = timezone.now()

    start_date = "2000-01-01"
    end_date = dataagora + timedelta(1)

    currentYear = date.today().year
    labels = []
    data = []
    aldeia = Aldeia.objects.filter(village__id = id)
    for entry in aldeia: 
        konta = DetailFamily.objects.filter(Q(population__date_register__range=(start_date, end_date)) & Q(status = True)  & Q(population__status_datap = 'ac') & Q(family__aldeia__id = entry.id)).count()
        labels.append(entry.name)
        data.append(konta)
    return JsonResponse(data={
		'labels':labels,
		'data':data,
		})


@login_required
def popchar_familyaldeia(request,id):
    currentYear = date.today().year
    labels = []
    data = []

    dataagora = timezone.now()

    tinan = date.today().year
    fulan = date.today().month
    year = date.today().year


    munisipiu_title = ""
    start_date = "2000-01-01"
    end_date = dataagora + timedelta(1)

    aldeia = Aldeia.objects.filter(village__id = id)
    for entry in aldeia: 
        konta = DetailFamily.objects.filter(Q(population__date_register__range=(start_date, end_date))  & Q(status = True) & Q(family__aldeia__id = entry.id) & Q(population__status_datap = 'ac')).values('family__municipality__name','family__municipality__id').annotate(count=Count('family__id')).order_by('family__id')

        labels.append(entry.name)
        data.append(len(konta))
        
    return JsonResponse(data={
		'labels':labels,
		'data':data,
		})


















