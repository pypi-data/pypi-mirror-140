from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from custom.models import Municipality,AdministrativePost,Village,Aldeia
from population.models import Population,DetailFamily,Family,Religion,Profession,Citizen,User,Migration,Death,Migrationout,Level_Education,Temporary
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
from datetime import datetime, timedelta
import calendar
from calendar import monthrange


from django.shortcuts import render,redirect

from population.utils import getfulan

from django.http import JsonResponse

@login_required
def reportb4jeral(request):
 

    fulan = getfulan()
    tinan = DetailFamily.objects.values(year=ExtractYear('population__date_register')).filter(Q(status = True)).annotate(total=Count('population__id')).order_by('year')
   
    munisipiu = Municipality.objects.all()
    postu = AdministrativePost.objects.all()
    suku = Village.objects.all()
    context = {
        'title': 'Populasaun Suku',
        'munisipiu' : munisipiu,
        'postu' : postu,
        'fulan' : fulan,
        'tinan' : tinan,
        'suku' : suku,
    }
    return render(request, 'population_report/b4/reportjeral-b4.html',context)






@login_required
def reportb4jeral_print(request):

    year = request.GET['tinan']
    fulan = request.GET['fulan']
    loronikus = monthrange(int(year), int(fulan))
    start_date = "2000-01-01"
    end_date = year + "-" +fulan+ "-"+"1"
    end_date_last = year + "-" +fulan+ "-"+str(loronikus[1])





    munisipiu = Municipality.objects.all()
    family_member = []

    for dadosmunisipiu in munisipiu.iterator() :

        # Hahu Quantidade populasaun Inisiu Fulan Ida ne’e
        #Qtd.Xefe Familia p1
        p1qxefefamilia = DetailFamily.objects.filter(Q(family_position = 1) & Q(population__status_datap = 'ac') & Q(population__date_register__range=(start_date, end_date)) &  Q(population__municipality__id = dadosmunisipiu.id) & Q(status = True)).count()
        
        #Estranjeiru Mane
        p1estrangeiromane  = Migration.objects.filter( Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 'm') & Q(population__status_datap = 'ac') & Q(population__municipality__id = dadosmunisipiu.id)).count()
        #Estranjeiru Feto

        p1estrangeirofeto  = Migration.objects.filter( Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 'f') & Q(population__status_datap = 'ac') & Q(population__municipality__id = dadosmunisipiu.id)).count()


        #populasaun suku laran Mane 
        p1tlsmane  = DetailFamily.objects.filter( Q(population__gender = 'm') & Q(status = True) 
        & Q(population__date_register__range=(start_date, end_date)) & Q(population__status_datap = 'ac') & Q(population__type_data = 'f') & Q(population__municipality__id = dadosmunisipiu.id)).count()
        #populasaun suku laran  Feto
        p1tlsfeto  = DetailFamily.objects.filter(Q(population__gender = 'f') & Q(status = True) & Q(population__type_data = 'f') & Q(population__date_register__range=(start_date, end_date)) & Q(population__status_datap = 'ac') & Q(population__municipality__id = dadosmunisipiu.id)).count()
        

        #populasaun suku migrasaun tls  mane
        p1tlsmane2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 'm') & Q(population__status_datap = 'ac') & Q(population__municipality__id = dadosmunisipiu.id)).count()
        #populasaun suku laran tls Feto
        p1tlsfeto2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 'f') & Q(population__status_datap = 'ac') & Q(population__municipality__id = dadosmunisipiu.id)).count()


        p1tlsmane = p1tlsmane + p1tlsmane2
        p1tlsfeto = p1tlsfeto + p1tlsfeto2

        #Quantidade membro Familia
        p1qmembrufamilia = DetailFamily.objects.filter(Q(status = True) & Q(population__status_datap = 'ac') & Q(population__date_register__range=(start_date, end_date)) & Q(population__municipality__id = dadosmunisipiu.id)).count()

        if p1qxefefamilia > p1qmembrufamilia :
            p1qmembrufamilia =   p1qxefefamilia - p1qmembrufamilia
        else : 
            p1qmembrufamilia =   p1qmembrufamilia - p1qxefefamilia




        #Quantidade Populasaun
        p1qpopulasaun = DetailFamily.objects.filter(Q(population__status_datap = 'ac') & Q(status = True) & Q(population__date_register__range=(start_date, end_date)) & Q(population__municipality__id = dadosmunisipiu.id)).count()




        #Aumenta
        # p3emorisemane = Migration.objects.filter(Q(family_position = 1) & Q(population__status_datap='ac') & Q(population__municipality__id = dadosmunisipiu.id)).count()
        #aumenta moris

        #Populasaun Etrangeiro Ne'ebe moris sexu mane temporario
        p3morisemane  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(population__gender = 'm')  & Q(population__municipality__id = dadosmunisipiu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()


        #Populasaun Etrangeiro Ne'ebe moris sexu feto temporario
        p3morisefeto  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(population__gender = 'f')  & Q(population__municipality__id = dadosmunisipiu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()




       #Populasaun timor Ne'ebe moris sexu mane temporario
        p3morisemanetemp  = Temporary.objects.filter(Q(cidadaunt = 1) & Q(population__gender = 'm')  & Q(population__municipality__id = dadosmunisipiu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()

        #Populasaun timor Ne'ebe moris sexu feto temporario
        p3morisefetotemp  = Temporary.objects.filter(Q(cidadaunt = 1) & Q(population__gender = 'f')  & Q(population__municipality__id = dadosmunisipiu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()

        #Populasaun timor oan ne'ebe muda no  moris sexu mane
        p3moristmane  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 'm')  & Q(population__municipality__id = dadosmunisipiu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
        #Populasaun timor oan ne'ebe muda no  moris sexu feto
        p3moristfeto  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 'f')  & Q(population__municipality__id = dadosmunisipiu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
        #Populasaun timor oan ne'ebe iha suku laran no  moris sexu mane
        p3moristmane2  = DetailFamily.objects.filter(Q(population__nationality = '1')  & Q(population__gender = 'm')  & Q(population__municipality__id = dadosmunisipiu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
        #Populasaun timor oan ne'ebe iha suku laran no  moris sexu feto
        p3moristfeto2  = DetailFamily.objects.filter(Q(population__nationality = '1')  & Q(population__gender = 'f')  & Q(population__municipality__id = dadosmunisipiu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()



        p3moristmane2 = p3moristmane + p3moristmane2 + p3morisemanetemp
        p3moristfeto2 = p3moristfeto + p3moristfeto2 + p3morisefetotemp

        #muda 
        #muda tama estrangeiro
        p3mudatamaemane  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__gender = 'm')  & Q(population__municipality__id = dadosmunisipiu.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()
        

        p3mudatamaefeto  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__gender = 'f')  & Q(population__municipality__id = dadosmunisipiu.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()

    


        p3mudatamatmane  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 'm')  & Q(population__municipality__id = dadosmunisipiu.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(from_aldeia__village__administrativepost__municipality__id = dadosmunisipiu.id).count()

        p3mudatamatfeto  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 'f')  & Q(population__municipality__id = dadosmunisipiu.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(from_aldeia__village__administrativepost__municipality__id = dadosmunisipiu.id).count()






        #menus mate
        # estrangeiro 
        
        p3mateemane  = Death.objects.filter(Q(population__nationality = '2') & Q(population__gender = 'm') & Q(population__status_datap = 'ma')  &  Q(population__municipality__id = dadosmunisipiu.id) & Q(date__year = year) & Q(date__month = fulan)).count()
        p3mateefeto  = Death.objects.filter(Q(population__nationality = '2') & Q(population__gender = 'f') & Q(population__status_datap = 'ma')  &  Q(population__municipality__id = dadosmunisipiu.id) & Q(date__year = year) & Q(date__month = fulan)).count()
       
       
       # timor 
        p3matetmane  = Death.objects.filter(Q(population__nationality = '1') & Q(population__gender = 'm') & Q(population__status_datap = 'ma')  &  Q(population__municipality__id = dadosmunisipiu.id) & Q(date__year = year) & Q(date__month = fulan)).count()
        p3matetfeto  = Death.objects.filter(Q(population__nationality = '1') & Q(population__gender = 'f') & Q(population__status_datap = 'ma')  &  Q(population__municipality__id = dadosmunisipiu.id) & Q(date__year = year) & Q(date__month = fulan)).count()




        #menus muda sai
        #estrageiro

        p3mudasaiemane  = Migrationout.objects.filter(Q(population__nationality = '2') & Q(population__gender = 'm') & Q(population__status_datap = 'mu')   & Q(population__municipality__id = dadosmunisipiu.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()

        p3mudasaiefeto  = Migrationout.objects.filter(Q(population__nationality = '2') & Q(population__gender = 'f') & Q(population__status_datap = 'mu')   & Q(population__municipality__id = dadosmunisipiu.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()


        p3mudasaitmane  = Migrationout.objects.filter(Q(population__nationality = '1') & Q(population__gender = 'm') & Q(population__status_datap = 'mu')   & Q(population__municipality__id = dadosmunisipiu.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(to_aldeia__village__administrativepost__municipality__id = dadosmunisipiu.id).count()

        p3mudasaitfeto  = Migrationout.objects.filter(Q(population__nationality = '1') & Q(population__gender = 'f') & Q(population__status_datap = 'mu')   & Q(population__municipality__id = dadosmunisipiu.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(to_aldeia__village__administrativepost__municipality__id = dadosmunisipiu.id).count()

    






        dataagora = end_date_last





    # Total Populasaun Fim do Mes



        # p3morisemane  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(population__gender = 'm')  & Q(population__municipality__id = dadosmunisipiu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='te')).count()


        # #Populasaun Etrangeiro Ne'ebe moris sexu feto temporario
        # p3morisefeto  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(population__gender = 'f')  & Q(population__municipality__id = dadosmunisipiu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='te')).count()




        #Estranjeiru Mane
        fimestrangeiromane  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 'm') & Q(population__status_datap = 'ac') & Q(population__municipality__id = dadosmunisipiu.id)).count()

        #Estranjeiru Feto
        fimestrangeirofeto  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 'f') & Q(population__status_datap = 'ac') & Q(population__municipality__id = dadosmunisipiu.id)).count()

        # fimestrangeiromane  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(date_arive__range=(start_date, dataagora)) & Q(population__gender = 'm') & Q(population__status_datap = 'te') & Q(population__municipality__id = dadosmunisipiu.id)).count()

    
        # fimestrangeirofeto  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(date_arive__range=(start_date, dataagora)) & Q(population__gender = 'f') & Q(population__status_datap = 'te') & Q(population__municipality__id = dadosmunisipiu.id)).count()





        #populasaun suku laran Mane 
        fimp1tlsmane  = DetailFamily.objects.filter(Q(population__gender = 'm') & Q(population__date_register__range=(start_date, dataagora))  & Q(status= True) & Q(population__status_datap = 'ac') & Q(population__type_data = 'f') & Q(population__municipality__id = dadosmunisipiu.id)).count()
        #populasaun suku laran  Feto
        fimp1tlsfeto  = DetailFamily.objects.filter(Q(population__gender = 'f') & Q(population__type_data = 'f') & Q(population__date_register__range=(start_date, dataagora))  & Q(status = True) & Q(population__status_datap = 'ac') & Q(population__municipality__id = dadosmunisipiu.id)).count()
        

        #populasaun suku migrasaun tls  mane
        fimp1tlsmane2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 'm') & Q(population__id_family='i') & Q(population__status_datap = 'ac') & Q(population__municipality__id = dadosmunisipiu.id)).count()
        #populasaun suku laran tls Feto
        fimp1tlsfeto2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 'f')  & Q(population__id_family='i') & Q(population__status_datap = 'ac') & Q(population__municipality__id = dadosmunisipiu.id)).count()


        fimp1tlsmane = fimp1tlsmane + fimp1tlsmane2
        fimp1tlsfeto = fimp1tlsfeto + fimp1tlsfeto2


        #Qtd.Xefe Familia
        fimp1qxefefamilia = DetailFamily.objects.filter(Q(family_position = 1) & Q(population__status_datap = 'ac') & Q(population__date_register__range=(start_date, dataagora)) & Q(population__id_family='i') &  Q(population__municipality__id = dadosmunisipiu.id)).count()
        

      #Quantidade membro Familia
        fimp1qmembrufamilia = DetailFamily.objects.filter(Q(status = True) 
        & Q(population__status_datap = 'ac') & Q(population__id_family='i') & Q(population__date_register__range=(start_date, dataagora)) & Q(population__municipality__id = dadosmunisipiu.id)).count()
        fimp1qmembrufamilia = fimp1qmembrufamilia - fimp1qxefefamilia

        #Quantidade Populasaun
        fimp1qpopulasaun = DetailFamily.objects.filter(Q(status = True) 
        & Q(population__status_datap = 'ac') & Q(population__id_family='i') & Q(population__date_register__range=(start_date, dataagora)) & Q(population__municipality__id = dadosmunisipiu.id)).count()






        family_member.append({
            'munisipiu' : dadosmunisipiu.name,
            'p1qxefefamilia' : p1qxefefamilia,
            'p1estrangeiromane' : p1estrangeiromane,
            'p1estrangeirofeto' : p1estrangeirofeto,
            'p1tlsmane' : p1tlsmane,
            'p1tlsfeto' : p1tlsfeto,
            'p1qmembrufamilia' : p1qmembrufamilia,
            'p1qpopulasaun' : p1qpopulasaun,

            #aumenta
            #Aumenta Moris
            #aumenta moris estrangiro mane,feto
            'p3morisemane' : p3morisemane,
            'p3morisefeto' : p3morisefeto,
            #aumenta moris Timor oan mane,feto
            'p3moristmane2' : p3moristmane2,
            'p3moristfeto2' : p3moristfeto2,
            
            #aumenta muda tama
            #muda tama estrageiro
            'p3mudatamaemane' : p3mudatamaemane,
            'p3mudatamaefeto' : p3mudatamaefeto,
            'p3mudatamatfeto' : p3mudatamatfeto,
            'p3mudatamatmane' : p3mudatamatmane,


            #menus 
            #menus mate 
            'p3mateemane' : p3mateemane,
            'p3mateefeto' : p3mateefeto,
            'p3matetmane' : p3matetmane,
            'p3matetfeto' : p3matetfeto,

            #menus muda sai
            'p3mudasaiefeto' : p3mudasaiefeto,
            'p3mudasaiemane' : p3mudasaiemane,

            'p3mudasaitfeto' : p3mudasaitfeto,
            'p3mudasaitmane' : p3mudasaitmane,


            #fim do mes
            #estrangeiro

            'fimestrangeiromane' : fimestrangeiromane,
            'fimestrangeirofeto' : fimestrangeirofeto,

            'fimp1tlsmane' : fimp1tlsmane,
            'fimp1tlsfeto' : fimp1tlsfeto,

            'fimp1qxefefamilia' : fimp1qxefefamilia,
            'fimp1qmembrufamilia' : fimp1qmembrufamilia,
            'fimp1qpopulasaun' : fimp1qpopulasaun,
            })
        
    template = "population_report/b4/reportjeral-b4-print.html"
    context = {
        'title' : 'Relatorio Dados Rekapitulasaun Populasaun',
        'family_member' : family_member,
        'year' : year,
        'fulan' : fulan,

    } 

    return render(request,template, context)













@login_required
def reportb4jeralmunisipiu_print(request):


    year = request.GET['tinan']
    fulan = request.GET['fulan']
    loronikus = monthrange(int(year), int(fulan))
    start_date = "2000-01-01"
    end_date = year + "-" +fulan+ "-"+"1"
    end_date_last = year + "-" +fulan+ "-"+str(loronikus[1])




    postu = AdministrativePost.objects.filter(municipality__id = request.GET['municipality'])
    family_member = []


    

    for dadospostu in postu.iterator() :
        munisipiu_title = dadospostu.municipality.name

        # Hahu Quantidade populasaun Inisiu Fulan Ida ne’e
        #Qtd.Xefe Familia p1
        p1qxefefamilia = DetailFamily.objects.filter(Q(family_position = 1) & Q(population__status_datap = 'ac') & Q(population__date_register__range=(start_date, end_date)) &  Q(population__administrativepost__id = dadospostu.id) & Q(status = True)).count()
        
        #Estranjeiru Mane
        p1estrangeiromane  = Migration.objects.filter( Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 'm') & Q(population__status_datap = 'ac') & Q(population__administrativepost__id = dadospostu.id)).count()
        #Estranjeiru Feto

        p1estrangeirofeto  = Migration.objects.filter( Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 'f') & Q(population__status_datap = 'ac') & Q(population__administrativepost__id = dadospostu.id)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p1estrangeiroseluk  = Migration.objects.filter( Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 's') & Q(population__status_datap = 'ac') & Q(population__administrativepost__id = dadospostu.id)).count()





        #populasaun suku laran Mane 
        p1tlsmane  = DetailFamily.objects.filter( Q(population__gender = 'm') & Q(status = True) 
        & Q(population__date_register__range=(start_date, end_date)) & Q(population__status_datap = 'ac') & Q(population__type_data = 'f') & Q(population__administrativepost__id = dadospostu.id)).count()
        #populasaun suku laran  Feto
        p1tlsfeto  = DetailFamily.objects.filter(Q(population__gender = 'f') & Q(status = True) & Q(population__type_data = 'f') & Q(population__date_register__range=(start_date, end_date)) & Q(population__status_datap = 'ac') & Q(population__administrativepost__id = dadospostu.id)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++ 
        p1tlsseluk  = DetailFamily.objects.filter(Q(population__gender = 's') & Q(status = True) & Q(population__type_data = 'f') & Q(population__date_register__range=(start_date, end_date)) & Q(population__status_datap = 'ac') & Q(population__administrativepost__id = dadospostu.id)).count()




        #populasaun suku migrasaun tls  mane
        p1tlsmane2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 'm') & Q(population__status_datap = 'ac') & Q(population__administrativepost__id = dadospostu.id)).count()
        #populasaun suku laran tls Feto
        p1tlsfeto2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 'f') & Q(population__status_datap = 'ac') & Q(population__administrativepost__id = dadospostu.id)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p1tlsseluk2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 's') & Q(population__status_datap = 'ac') & Q(population__administrativepost__id = dadospostu.id)).count()



        p1tlsmane = p1tlsmane + p1tlsmane2
        p1tlsfeto = p1tlsfeto + p1tlsfeto2
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p1tlsseluk = p1tlsseluk + p1tlsseluk2

        #Quantidade membro Familia
        p1qmembrufamilia = DetailFamily.objects.filter(Q(status = True) & Q(population__status_datap = 'ac') & Q(population__date_register__range=(start_date, end_date)) & Q(population__administrativepost__id = dadospostu.id)).count()

        if p1qxefefamilia > p1qmembrufamilia :
            p1qmembrufamilia =   p1qxefefamilia - p1qmembrufamilia
        else : 
            p1qmembrufamilia =   p1qmembrufamilia - p1qxefefamilia




        #Quantidade Populasaun
        p1qpopulasaun = DetailFamily.objects.filter(Q(population__status_datap = 'ac') & Q(status = True) & Q(population__date_register__range=(start_date, end_date)) & Q(population__administrativepost__id = dadospostu.id)).count()




        #Aumenta
        # p3emorisemane = Migration.objects.filter(Q(family_position = 1) & Q(population__status_datap='ac') & Q(population__administrativepost__id = dadospostu.id)).count()
        #aumenta moris

        #Populasaun Etrangeiro Ne'ebe moris sexu mane temporario
        p3morisemane  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(population__gender = 'm')  & Q(population__administrativepost__id = dadospostu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()
        #Populasaun Etrangeiro Ne'ebe moris sexu feto temporario
        p3morisefeto  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(population__gender = 'f')  & Q(population__administrativepost__id = dadospostu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3moriseseluk  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(population__gender = 's')  & Q(population__administrativepost__id = dadospostu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()
 



       #Populasaun timor Ne'ebe moris sexu mane temporario
        p3morisemanetemp  = Temporary.objects.filter(Q(cidadaunt = 1) & Q(population__gender = 'm')  & Q(population__administrativepost__id = dadospostu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()
        #Populasaun timor Ne'ebe moris sexu feto temporario
        p3morisefetotemp  = Temporary.objects.filter(Q(cidadaunt = 1) & Q(population__gender = 'f')  & Q(population__administrativepost__id = dadospostu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3moriseseluktemp  = Temporary.objects.filter(Q(cidadaunt = 1) & Q(population__gender = 's')  & Q(population__administrativepost__id = dadospostu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()
    



        #Populasaun timor oan ne'ebe muda no  moris sexu mane
        p3moristmane  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 'm')  & Q(population__administrativepost__id = dadospostu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
        #Populasaun timor oan ne'ebe muda no  moris sexu feto
        p3moristfeto  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 'f')  & Q(population__administrativepost__id = dadospostu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++        
        p3moristseluk  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 's')  & Q(population__administrativepost__id = dadospostu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
              #Populasaun timor oan ne'ebe iha suku laran no  moris sexu mane
        


        #Populasaun timor oan ne'ebe iha suku laran no  moris sexu mane
        p3moristmane2  = DetailFamily.objects.filter(Q(population__nationality = '1')  & Q(population__gender = 'm')  & Q(population__administrativepost__id = dadospostu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
        #Populasaun timor oan ne'ebe iha suku laran no  moris sexu feto
        p3moristfeto2  = DetailFamily.objects.filter(Q(population__nationality = '1')  & Q(population__gender = 'f')  & Q(population__administrativepost__id = dadospostu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3moristseluk2  = DetailFamily.objects.filter(Q(population__nationality = '1')  & Q(population__gender = 's')  & Q(population__administrativepost__id = dadospostu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
    



        p3moristmane2 = p3moristmane + p3moristmane2 + p3morisemanetemp
        p3moristfeto2 = p3moristfeto + p3moristfeto2 + p3morisefetotemp
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3moristseluk2 = p3moristseluk + p3moristseluk2 + p3moriseseluktemp




        #muda 
        #muda tama estrangeiro
        p3mudatamaemane  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__gender = 'm')  & Q(population__administrativepost__id = dadospostu.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()
        p3mudatamaefeto  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__gender = 'f')  & Q(population__administrativepost__id = dadospostu.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3mudatamaeseluk  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__gender = 's')  & Q(population__administrativepost__id = dadospostu.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()
  

    
        p3mudatamatmane  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 'm')  & Q(population__administrativepost__id = dadospostu.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(from_aldeia__village__administrativepost__id = dadospostu.id).count()
        p3mudatamatfeto  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 'f')  & Q(population__administrativepost__id = dadospostu.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(from_aldeia__village__administrativepost__id = dadospostu.id).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3mudatamatseluk  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 's')  & Q(population__administrativepost__id = dadospostu.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(from_aldeia__village__administrativepost__id = dadospostu.id).count()
    



        #menus mate
        # estrangeiro 
        
        p3mateemane  = Death.objects.filter(Q(population__nationality = '2') & Q(population__gender = 'm') & Q(population__status_datap = 'ma')  &  Q(population__administrativepost__id = dadospostu.id) & Q(date__year = year) & Q(date__month = fulan)).count()
        p3mateefeto  = Death.objects.filter(Q(population__nationality = '2') & Q(population__gender = 'f') & Q(population__status_datap = 'ma')  &  Q(population__administrativepost__id = dadospostu.id) & Q(date__year = year) & Q(date__month = fulan)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3mateeseluk  = Death.objects.filter(Q(population__nationality = '2') & Q(population__gender = 's') & Q(population__status_datap = 'ma')  &  Q(population__administrativepost__id = dadospostu.id) & Q(date__year = year) & Q(date__month = fulan)).count()
        
       
       
       # timor 
        p3matetmane  = Death.objects.filter(Q(population__nationality = '1') & Q(population__gender = 'm') & Q(population__status_datap = 'ma')  &  Q(population__administrativepost__id = dadospostu.id) & Q(date__year = year) & Q(date__month = fulan)).count()
        p3matetfeto  = Death.objects.filter(Q(population__nationality = '1') & Q(population__gender = 'f') & Q(population__status_datap = 'ma')  &  Q(population__administrativepost__id = dadospostu.id) & Q(date__year = year) & Q(date__month = fulan)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3matetseluk  = Death.objects.filter(Q(population__nationality = '1') & Q(population__gender = 's') & Q(population__status_datap = 'ma')  &  Q(population__administrativepost__id = dadospostu.id) & Q(date__year = year) & Q(date__month = fulan)).count()
     


        #menus muda sai
        #estrageiro

        p3mudasaiemane  = Migrationout.objects.filter(Q(population__nationality = '2') & Q(population__gender = 'm') & Q(population__status_datap = 'mu')   & Q(population__administrativepost__id = dadospostu.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()
        p3mudasaiefeto  = Migrationout.objects.filter(Q(population__nationality = '2') & Q(population__gender = 'f') & Q(population__status_datap = 'mu')   & Q(population__administrativepost__id = dadospostu.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3mudasaieseluk  = Migrationout.objects.filter(Q(population__nationality = '2') & Q(population__gender = 's') & Q(population__status_datap = 'mu')   & Q(population__administrativepost__id = dadospostu.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()
     

        p3mudasaitmane  = Migrationout.objects.filter(Q(population__nationality = '1') & Q(population__gender = 'm') & Q(population__status_datap = 'mu')   & Q(population__administrativepost__id = dadospostu.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(to_aldeia__village__administrativepost__id = dadospostu.id).count()
        p3mudasaitfeto  = Migrationout.objects.filter(Q(population__nationality = '1') & Q(population__gender = 'f') & Q(population__status_datap = 'mu')   & Q(population__administrativepost__id = dadospostu.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(to_aldeia__village__administrativepost__id = dadospostu.id).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3mudasaitseluk  = Migrationout.objects.filter(Q(population__nationality = '1') & Q(population__gender = 's') & Q(population__status_datap = 'mu')   & Q(population__administrativepost__id = dadospostu.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(to_aldeia__village__administrativepost__id = dadospostu.id).count()
      
    






        dataagora = end_date_last





    # Total Populasaun Fim do Mes



        # p3morisemane  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(population__gender = 'm')  & Q(population__administrativepost__id = dadospostu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='te')).count()


        # #Populasaun Etrangeiro Ne'ebe moris sexu feto temporario
        # p3morisefeto  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(population__gender = 'f')  & Q(population__administrativepost__id = dadospostu.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='te')).count()




        #Estranjeiru Mane
        fimestrangeiromane  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 'm') & Q(population__status_datap = 'ac') & Q(population__administrativepost__id = dadospostu.id)).count()

        #Estranjeiru Feto
        fimestrangeirofeto  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 'f') & Q(population__status_datap = 'ac') & Q(population__administrativepost__id = dadospostu.id)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        fimestrangeiroseluk  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 's') & Q(population__status_datap = 'ac') & Q(population__administrativepost__id = dadospostu.id)).count()
       
        # fimestrangeiromane  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(date_arive__range=(start_date, dataagora)) & Q(population__gender = 'm') & Q(population__status_datap = 'te') & Q(population__administrativepost__id = dadospostu.id)).count()

    
        # fimestrangeirofeto  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(date_arive__range=(start_date, dataagora)) & Q(population__gender = 'f') & Q(population__status_datap = 'te') & Q(population__administrativepost__id = dadospostu.id)).count()





        #populasaun suku laran Mane 
        fimp1tlsmane  = DetailFamily.objects.filter(Q(population__gender = 'm') & Q(population__date_register__range=(start_date, dataagora))  & Q(status= True) & Q(population__status_datap = 'ac') & Q(population__type_data = 'f') & Q(population__administrativepost__id = dadospostu.id)).count()
        #populasaun suku laran  Feto
        fimp1tlsfeto  = DetailFamily.objects.filter(Q(population__gender = 'f') & Q(population__type_data = 'f') & Q(population__date_register__range=(start_date, dataagora))  & Q(status = True) & Q(population__status_datap = 'ac') & Q(population__administrativepost__id = dadospostu.id)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        fimp1tlsseluk  = DetailFamily.objects.filter(Q(population__gender = 's') & Q(population__type_data = 'f') & Q(population__date_register__range=(start_date, dataagora))  & Q(status = True) & Q(population__status_datap = 'ac') & Q(population__administrativepost__id = dadospostu.id)).count()


        #populasaun suku migrasaun tls  mane
        fimp1tlsmane2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 'm') & Q(population__id_family='i') & Q(population__status_datap = 'ac') & Q(population__administrativepost__id = dadospostu.id)).count()
        #populasaun suku laran tls Feto
        fimp1tlsfeto2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 'f')  & Q(population__id_family='i') & Q(population__status_datap = 'ac') & Q(population__administrativepost__id = dadospostu.id)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        fimp1tlsseluk2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 's')  & Q(population__id_family='i') & Q(population__status_datap = 'ac') & Q(population__administrativepost__id = dadospostu.id)).count()
     

        fimp1tlsmane = fimp1tlsmane + fimp1tlsmane2
        fimp1tlsfeto = fimp1tlsfeto + fimp1tlsfeto2
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        fimp1tlsseluk = fimp1tlsseluk + fimp1tlsseluk2


        #Qtd.Xefe Familia
        fimp1qxefefamilia = DetailFamily.objects.filter(Q(family_position = 1) & Q(population__status_datap = 'ac') & Q(population__date_register__range=(start_date, dataagora)) & Q(population__id_family='i') &  Q(population__administrativepost__id = dadospostu.id)).count()
        

      #Quantidade membro Familia
        fimp1qmembrufamilia = DetailFamily.objects.filter(Q(status = True) 
        & Q(population__status_datap = 'ac') & Q(population__id_family='i') & Q(population__date_register__range=(start_date, dataagora)) & Q(population__administrativepost__id = dadospostu.id)).count()
        fimp1qmembrufamilia = fimp1qmembrufamilia - fimp1qxefefamilia

        #Quantidade Populasaun
        fimp1qpopulasaun = DetailFamily.objects.filter(Q(status = True) 
        & Q(population__status_datap = 'ac') & Q(population__id_family='i') & Q(population__date_register__range=(start_date, dataagora)) & Q(population__administrativepost__id = dadospostu.id)).count()






        family_member.append({
            'munisipiu' : dadospostu.municipality.name,
            'postu' : dadospostu.name,
            'p1qxefefamilia' : p1qxefefamilia,
            #Populasaun Estrangeiru
            'p1estrangeiromane' : p1estrangeiromane,
            'p1estrangeirofeto' : p1estrangeirofeto,
            'p1estrangeiroseluk' : p1estrangeiroseluk,

            #populasaun Suku
            'p1tlsmane' : p1tlsmane,
            'p1tlsfeto' : p1tlsfeto,
            'p1tlsseluk' : p1tlsseluk,


            'p1qmembrufamilia' : p1qmembrufamilia,
            'p1qpopulasaun' : p1qpopulasaun,

            #aumenta
            #Aumenta Moris
            #aumenta moris estrangiro mane,feto
            'p3morisemane' : p3morisemane,
            'p3morisefeto' : p3morisefeto,
            'p3moriseseluk' : p3moriseseluk,

            
            #aumenta moris Timor oan mane,feto
            'p3moristmane2' : p3moristmane2,
            'p3moristfeto2' : p3moristfeto2,
            'p3moristseluk2' : p3moristseluk2,
            



            #aumenta muda tama
            #muda tama estrageiro
            'p3mudatamaemane' : p3mudatamaemane,
            'p3mudatamaefeto' : p3mudatamaefeto,
            'p3mudatamaeseluk' : p3mudatamaeseluk,


            'p3mudatamatfeto' : p3mudatamatfeto,
            'p3mudatamatmane' : p3mudatamatmane,
            'p3mudatamatseluk' : p3mudatamatseluk,

            #menus 
            #menus mate 
            'p3mateemane' : p3mateemane,
            'p3mateefeto' : p3mateefeto,
            'p3mateeseluk' : p3mateeseluk,

            'p3matetmane' : p3matetmane,
            'p3matetfeto' : p3matetfeto,
            'p3matetseluk' : p3matetseluk,

            #menus muda sai
            'p3mudasaiefeto' : p3mudasaiefeto,
            'p3mudasaiemane' : p3mudasaiemane,
            'p3mudasaieseluk' : p3mudasaieseluk,

            'p3mudasaitfeto' : p3mudasaitfeto,
            'p3mudasaitmane' : p3mudasaitmane,
            'p3mudasaitseluk' : p3mudasaieseluk,


            #fim do mes
            #estrangeiro

            'fimestrangeiromane' : fimestrangeiromane,
            'fimestrangeirofeto' : fimestrangeirofeto,
            'fimestrangeiroseluk' : fimestrangeirofeto,

            'fimp1tlsmane' : fimp1tlsmane,
            'fimp1tlsfeto' : fimp1tlsfeto,
            'fimp1tlsseluk' : fimp1tlsseluk,

            'fimp1qxefefamilia' : fimp1qxefefamilia,
            'fimp1qmembrufamilia' : fimp1qmembrufamilia,
            'fimp1qpopulasaun' : fimp1qpopulasaun,

            })

  
    template = "population_report/b4/reportjeralmunisipiu-b4-print.html"
    context = {
        'title' : 'Relatorio Dados Rekapitulasaun Populasaun',
        'family_member' : family_member,
        'year' : year,
        'munisipiu_title' : munisipiu_title.upper(),
        'fulan' :  fulan,

    } 

    return render(request,template, context)








@login_required
def reportb4jeralpostu_print(request):


    year = request.GET['tinan']
    fulan = request.GET['fulan']
    loronikus = monthrange(int(year), int(fulan))
    start_date = "2000-01-01"
    end_date = year + "-" +fulan+ "-"+"1"
    end_date_last = year + "-" +fulan+ "-"+str(loronikus[1])



    suku = Village.objects.filter(administrativepost__id = request.GET['administrativepost'])
    family_member = []


    

    for dadossuku in suku.iterator() :
        munisipiu_title = dadossuku.administrativepost.municipality.name
        postu_title = dadossuku.administrativepost.name

        # Hahu Quantidade populasaun Inisiu Fulan Ida ne’e
        #Qtd.Xefe Familia p1
        p1qxefefamilia = DetailFamily.objects.filter(Q(family_position = 1) & Q(population__status_datap = 'ac') & Q(population__date_register__range=(start_date, end_date)) &  Q(population__village__id = dadossuku.id) & Q(status = True)).count()
        
        #Estranjeiru Mane
        p1estrangeiromane  = Migration.objects.filter( Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 'm') & Q(population__status_datap = 'ac') & Q(population__village__id = dadossuku.id)).count()
        #Estranjeiru Feto
        p1estrangeirofeto  = Migration.objects.filter( Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 'f') & Q(population__status_datap = 'ac') & Q(population__village__id = dadossuku.id)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p1estrangeiroseluk  = Migration.objects.filter( Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 's') & Q(population__status_datap = 'ac') & Q(population__village__id = dadossuku.id)).count()
   


        #populasaun suku laran Mane 
        p1tlsmane  = DetailFamily.objects.filter( Q(population__gender = 'm') & Q(status = True) 
        & Q(population__date_register__range=(start_date, end_date)) & Q(population__status_datap = 'ac') & Q(population__type_data = 'f') & Q(population__village__id = dadossuku.id)).count()
        #populasaun suku laran  Feto
        p1tlsfeto  = DetailFamily.objects.filter(Q(population__gender = 'f') & Q(status = True) & Q(population__type_data = 'f') & Q(population__date_register__range=(start_date, end_date)) & Q(population__status_datap = 'ac') & Q(population__village__id = dadossuku.id)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++ 
        p1tlsseluk  = DetailFamily.objects.filter(Q(population__gender = 's') & Q(status = True) & Q(population__type_data = 'f') & Q(population__date_register__range=(start_date, end_date)) & Q(population__status_datap = 'ac') & Q(population__village__id = dadossuku.id)).count()
    


        #populasaun suku migrasaun tls  mane
        p1tlsmane2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 'm') & Q(population__status_datap = 'ac') & Q(population__village__id = dadossuku.id)).count()
        #populasaun suku laran tls Feto
        p1tlsfeto2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 'f') & Q(population__status_datap = 'ac') & Q(population__village__id = dadossuku.id)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p1tlsseluk2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 's') & Q(population__status_datap = 'ac') & Q(population__village__id = dadossuku.id)).count()
      


        p1tlsmane = p1tlsmane + p1tlsmane2
        p1tlsfeto = p1tlsfeto + p1tlsfeto2
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p1tlsseluk = p1tlsseluk + p1tlsseluk2





        #Quantidade membro Familia
        p1qmembrufamilia = DetailFamily.objects.filter(Q(status = True) & Q(population__status_datap = 'ac') & Q(population__date_register__range=(start_date, end_date)) & Q(population__village__id = dadossuku.id)).count()

        if p1qxefefamilia > p1qmembrufamilia :
            p1qmembrufamilia =   p1qxefefamilia - p1qmembrufamilia
        else : 
            p1qmembrufamilia =   p1qmembrufamilia - p1qxefefamilia




        #Quantidade Populasaun
        p1qpopulasaun = DetailFamily.objects.filter(Q(population__status_datap = 'ac') & Q(status = True) & Q(population__date_register__range=(start_date, end_date)) & Q(population__village__id = dadossuku.id)).count()




        #Aumenta
        # p3emorisemane = Migration.objects.filter(Q(family_position = 1) & Q(population__status_datap='ac') & Q(population__village__id = dadossuku.id)).count()
        #aumenta moris

        #Populasaun Etrangeiro Ne'ebe moris sexu mane temporario
        p3morisemane  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(population__gender = 'm')  & Q(population__village__id = dadossuku.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()
        #Populasaun Etrangeiro Ne'ebe moris sexu feto temporario
        p3morisefeto  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(population__gender = 'f')  & Q(population__village__id = dadossuku.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3moriseseluk  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(population__gender = 's')  & Q(population__village__id = dadossuku.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()
        



       #Populasaun timor Ne'ebe moris sexu mane temporario
        p3morisemanetemp  = Temporary.objects.filter(Q(cidadaunt = 1) & Q(population__gender = 'm')  & Q(population__village__id = dadossuku.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()
        #Populasaun timor Ne'ebe moris sexu feto temporario
        p3morisefetotemp  = Temporary.objects.filter(Q(cidadaunt = 1) & Q(population__gender = 'f')  & Q(population__village__id = dadossuku.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3moriseseluktemp  = Temporary.objects.filter(Q(cidadaunt = 1) & Q(population__gender = 's')  & Q(population__village__id = dadossuku.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()
     


        #Populasaun timor oan ne'ebe muda no  moris sexu mane
        p3moristmane  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 'm')  & Q(population__village__id = dadossuku.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
        #Populasaun timor oan ne'ebe muda no  moris sexu feto
        p3moristfeto  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 'f')  & Q(population__village__id = dadossuku.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++        
        p3moristseluk  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 's')  & Q(population__village__id = dadossuku.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
       #Populasaun timor oan ne'ebe iha suku laran no  moris sexu mane
        



        #Populasaun timor oan ne'ebe iha suku laran no  moris sexu mane
        p3moristmane2  = DetailFamily.objects.filter(Q(population__nationality = '1')  & Q(population__gender = 'm')  & Q(population__village__id = dadossuku.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
        #Populasaun timor oan ne'ebe iha suku laran no  moris sexu feto
        p3moristfeto2  = DetailFamily.objects.filter(Q(population__nationality = '1')  & Q(population__gender = 'f')  & Q(population__village__id = dadossuku.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3moristseluk2  = DetailFamily.objects.filter(Q(population__nationality = '1')  & Q(population__gender = 's')  & Q(population__village__id = dadossuku.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
     


        p3moristmane2 = p3moristmane + p3moristmane2 + p3morisemanetemp
        p3moristfeto2 = p3moristfeto + p3moristfeto2 + p3morisefetotemp
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3moristseluk2 = p3moristseluk + p3moristseluk2 + p3moriseseluktemp





        #muda 
        #muda tama estrangeiro
        p3mudatamaemane  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__gender = 'm')  & Q(population__village__id = dadossuku.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()
        p3mudatamaefeto  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__gender = 'f')  & Q(population__village__id = dadossuku.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3mudatamaeseluk  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__gender = 's')  & Q(population__village__id = dadossuku.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()
     
    
        p3mudatamatmane  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 'm')  & Q(population__village__id = dadossuku.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(from_aldeia__village__id = dadossuku.id).count()
        p3mudatamatfeto  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 'f')  & Q(population__village__id = dadossuku.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(from_aldeia__village__id = dadossuku.id).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3mudatamatseluk  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 's')  & Q(population__village__id = dadossuku.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(from_aldeia__village__id = dadossuku.id).count()
    






        #menus mate
        # estrangeiro 
        
        p3mateemane  = Death.objects.filter(Q(population__nationality = '2') & Q(population__gender = 'm') & Q(population__status_datap = 'ma')  &  Q(population__village__id = dadossuku.id) & Q(date__year = year) & Q(date__month = fulan)).count()
        p3mateefeto  = Death.objects.filter(Q(population__nationality = '2') & Q(population__gender = 'f') & Q(population__status_datap = 'ma')  &  Q(population__village__id = dadossuku.id) & Q(date__year = year) & Q(date__month = fulan)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3mateeseluk  = Death.objects.filter(Q(population__nationality = '2') & Q(population__gender = 's') & Q(population__status_datap = 'ma')  &  Q(population__village__id = dadossuku.id) & Q(date__year = year) & Q(date__month = fulan)).count()
     
       
       # timor 
        p3matetmane  = Death.objects.filter(Q(population__nationality = '1') & Q(population__gender = 'm') & Q(population__status_datap = 'ma')  &  Q(population__village__id = dadossuku.id) & Q(date__year = year) & Q(date__month = fulan)).count()
        p3matetfeto  = Death.objects.filter(Q(population__nationality = '1') & Q(population__gender = 'f') & Q(population__status_datap = 'ma')  &  Q(population__village__id = dadossuku.id) & Q(date__year = year) & Q(date__month = fulan)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3matetseluk  = Death.objects.filter(Q(population__nationality = '1') & Q(population__gender = 's') & Q(population__status_datap = 'ma')  &  Q(population__village__id = dadossuku.id) & Q(date__year = year) & Q(date__month = fulan)).count()
     



        #menus muda sai
        #estrageiro

        p3mudasaiemane  = Migrationout.objects.filter(Q(population__nationality = '2') & Q(population__gender = 'm') & Q(population__status_datap = 'mu')   & Q(population__village__id = dadossuku.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()
        p3mudasaiefeto  = Migrationout.objects.filter(Q(population__nationality = '2') & Q(population__gender = 'f') & Q(population__status_datap = 'mu')   & Q(population__village__id = dadossuku.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3mudasaieseluk  = Migrationout.objects.filter(Q(population__nationality = '2') & Q(population__gender = 's') & Q(population__status_datap = 'mu')   & Q(population__village__id = dadossuku.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()
      



        p3mudasaitmane  = Migrationout.objects.filter(Q(population__nationality = '1') & Q(population__gender = 'm') & Q(population__status_datap = 'mu')   & Q(population__village__id = dadossuku.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(to_aldeia__village__id = dadossuku.id).count()
        p3mudasaitfeto  = Migrationout.objects.filter(Q(population__nationality = '1') & Q(population__gender = 'f') & Q(population__status_datap = 'mu')   & Q(population__village__id = dadossuku.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(to_aldeia__village__id = dadossuku.id).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3mudasaitseluk  = Migrationout.objects.filter(Q(population__nationality = '1') & Q(population__gender = 's') & Q(population__status_datap = 'mu')   & Q(population__village__id = dadossuku.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(to_aldeia__village__id = dadossuku.id).count()
     

    






        dataagora = end_date_last





    # Total Populasaun Fim do Mes



        # p3morisemane  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(population__gender = 'm')  & Q(population__village__id = dadossuku.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='te')).count()


        # #Populasaun Etrangeiro Ne'ebe moris sexu feto temporario
        # p3morisefeto  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(population__gender = 'f')  & Q(population__village__id = dadossuku.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='te')).count()




        #Estranjeiru Mane
        fimestrangeiromane  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 'm') & Q(population__status_datap = 'ac') & Q(population__village__id = dadossuku.id)).count()
        #Estranjeiru Feto
        fimestrangeirofeto  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 'f') & Q(population__status_datap = 'ac') & Q(population__village__id = dadossuku.id)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        fimestrangeiroseluk  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 's') & Q(population__status_datap = 'ac') & Q(population__village__id = dadossuku.id)).count()
   
        # fimestrangeiromane  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(date_arive__range=(start_date, dataagora)) & Q(population__gender = 'm') & Q(population__status_datap = 'te') & Q(population__village__id = dadossuku.id)).count()

    
        # fimestrangeirofeto  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(date_arive__range=(start_date, dataagora)) & Q(population__gender = 'f') & Q(population__status_datap = 'te') & Q(population__village__id = dadossuku.id)).count()





        #populasaun suku laran Mane 
        fimp1tlsmane  = DetailFamily.objects.filter(Q(population__gender = 'm') & Q(population__date_register__range=(start_date, dataagora))  & Q(status= True) & Q(population__status_datap = 'ac') & Q(population__type_data = 'f') & Q(population__village__id = dadossuku.id)).count()
        #populasaun suku laran  Feto
        fimp1tlsfeto  = DetailFamily.objects.filter(Q(population__gender = 'f') & Q(population__type_data = 'f') & Q(population__date_register__range=(start_date, dataagora))  & Q(status = True) & Q(population__status_datap = 'ac') & Q(population__village__id = dadossuku.id)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        fimp1tlsseluk  = DetailFamily.objects.filter(Q(population__gender = 's') & Q(population__type_data = 'f') & Q(population__date_register__range=(start_date, dataagora))  & Q(status = True) & Q(population__status_datap = 'ac') & Q(population__village__id = dadossuku.id)).count()
   


        #populasaun suku migrasaun tls  mane
        fimp1tlsmane2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 'm') & Q(population__id_family='i') & Q(population__status_datap = 'ac') & Q(population__village__id = dadossuku.id)).count()
        #populasaun suku laran tls Feto
        fimp1tlsfeto2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 'f')  & Q(population__id_family='i') & Q(population__status_datap = 'ac') & Q(population__village__id = dadossuku.id)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        fimp1tlsseluk2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 's')  & Q(population__id_family='i') & Q(population__status_datap = 'ac') & Q(population__village__id = dadossuku.id)).count()
      



        fimp1tlsmane = fimp1tlsmane + fimp1tlsmane2
        fimp1tlsfeto = fimp1tlsfeto + fimp1tlsfeto2
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        fimp1tlsseluk = fimp1tlsseluk + fimp1tlsseluk2

        #Qtd.Xefe Familia
        fimp1qxefefamilia = DetailFamily.objects.filter(Q(family_position = 1) & Q(population__status_datap = 'ac') & Q(population__date_register__range=(start_date, dataagora)) & Q(population__id_family='i') &  Q(population__village__id = dadossuku.id)).count()
        

      #Quantidade membro Familia
        fimp1qmembrufamilia = DetailFamily.objects.filter(Q(status = True) 
        & Q(population__status_datap = 'ac') & Q(population__id_family='i') & Q(population__date_register__range=(start_date, dataagora)) & Q(population__village__id = dadossuku.id)).count()
        fimp1qmembrufamilia = fimp1qmembrufamilia - fimp1qxefefamilia

        #Quantidade Populasaun
        fimp1qpopulasaun = DetailFamily.objects.filter(Q(status = True) 
        & Q(population__status_datap = 'ac') & Q(population__id_family='i') & Q(population__date_register__range=(start_date, dataagora)) & Q(population__village__id = dadossuku.id)).count()






        family_member.append({
     
            'suku' : dadossuku.name,
            'p1qxefefamilia' : p1qxefefamilia,
            #Populasaun Estrangeiru
            'p1estrangeiromane' : p1estrangeiromane,
            'p1estrangeirofeto' : p1estrangeirofeto,
            'p1estrangeiroseluk' : p1estrangeiroseluk,

            #populasaun Suku
            'p1tlsmane' : p1tlsmane,
            'p1tlsfeto' : p1tlsfeto,
            'p1tlsseluk' : p1tlsseluk,


            'p1qmembrufamilia' : p1qmembrufamilia,
            'p1qpopulasaun' : p1qpopulasaun,

            #aumenta
            #Aumenta Moris
            #aumenta moris estrangiro mane,feto
            'p3morisemane' : p3morisemane,
            'p3morisefeto' : p3morisefeto,
            'p3moriseseluk' : p3moriseseluk,

            
            #aumenta moris Timor oan mane,feto
            'p3moristmane2' : p3moristmane2,
            'p3moristfeto2' : p3moristfeto2,
            'p3moristseluk2' : p3moristseluk2,
            



            #aumenta muda tama
            #muda tama estrageiro
            'p3mudatamaemane' : p3mudatamaemane,
            'p3mudatamaefeto' : p3mudatamaefeto,
            'p3mudatamaeseluk' : p3mudatamaeseluk,


            'p3mudatamatfeto' : p3mudatamatfeto,
            'p3mudatamatmane' : p3mudatamatmane,
            'p3mudatamatseluk' : p3mudatamatseluk,

            #menus 
            #menus mate 
            'p3mateemane' : p3mateemane,
            'p3mateefeto' : p3mateefeto,
            'p3mateeseluk' : p3mateeseluk,

            'p3matetmane' : p3matetmane,
            'p3matetfeto' : p3matetfeto,
            'p3matetseluk' : p3matetseluk,

            #menus muda sai
            'p3mudasaiefeto' : p3mudasaiefeto,
            'p3mudasaiemane' : p3mudasaiemane,
            'p3mudasaieseluk' : p3mudasaieseluk,

            'p3mudasaitfeto' : p3mudasaitfeto,
            'p3mudasaitmane' : p3mudasaitmane,
            'p3mudasaitseluk' : p3mudasaieseluk,


            #fim do mes
            #estrangeiro

            'fimestrangeiromane' : fimestrangeiromane,
            'fimestrangeirofeto' : fimestrangeirofeto,
            'fimestrangeiroseluk' : fimestrangeirofeto,

            'fimp1tlsmane' : fimp1tlsmane,
            'fimp1tlsfeto' : fimp1tlsfeto,
            'fimp1tlsseluk' : fimp1tlsseluk,

            'fimp1qxefefamilia' : fimp1qxefefamilia,
            'fimp1qmembrufamilia' : fimp1qmembrufamilia,
            'fimp1qpopulasaun' : fimp1qpopulasaun,



            })
  
    template = "population_report/b4/reportjeralpostu-b4-print.html"
    context = {
        'title' : 'Relatorio Dados Rekapitulasaun Populasaun',
        'family_member' : family_member,
        'year' : year,
        'fulan' : fulan,
        'munisipiu_title' : munisipiu_title.upper(),
        'postu_title' : postu_title.upper(),

    } 

    return render(request,template, context)

























@login_required
def reportb4jeralsuku_print(request):


    year = request.GET['tinan']
    fulan = request.GET['fulan']
    loronikus = monthrange(int(year), int(fulan))
    start_date = "2000-01-01"
    end_date = year + "-" +fulan+ "-"+"1"
    end_date_last = year + "-" +fulan+ "-"+str(loronikus[1])



    aldeia = Aldeia.objects.filter(village__id = request.GET['village'])
    family_member = []


    

    for dadosaldeia in aldeia.iterator() :
        munisipiu_title = dadosaldeia.village.administrativepost.municipality.name
        postu_title = dadosaldeia.village.administrativepost.name
        suku_title = dadosaldeia.village.name

        # Hahu Quantidade populasaun Inisiu Fulan Ida ne’e
        #Qtd.Xefe Familia p1
        p1qxefefamilia = DetailFamily.objects.filter(Q(family_position = 1) & Q(population__status_datap = 'ac') & Q(population__date_register__range=(start_date, end_date)) &  Q(population__aldeia__id = dadosaldeia.id) & Q(status = True)).count()
        
        #Estranjeiru Mane
        p1estrangeiromane  = Migration.objects.filter( Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 'm') & Q(population__status_datap = 'ac') & Q(population__aldeia__id = dadosaldeia.id)).count()
        #Estranjeiru Feto

        p1estrangeirofeto  = Migration.objects.filter( Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 'f') & Q(population__status_datap = 'ac') & Q(population__aldeia__id = dadosaldeia.id)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p1estrangeiroseluk  = Migration.objects.filter( Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 's') & Q(population__status_datap = 'ac') & Q(population__aldeia__id = dadosaldeia.id)).count()
      



        #populasaun suku laran Mane 
        p1tlsmane  = DetailFamily.objects.filter( Q(population__gender = 'm') & Q(status = True) 
        & Q(population__date_register__range=(start_date, end_date)) & Q(population__status_datap = 'ac') & Q(population__type_data = 'f') & Q(population__aldeia__id = dadosaldeia.id)).count()
        #populasaun suku laran  Feto
        p1tlsfeto  = DetailFamily.objects.filter(Q(population__gender = 'f') & Q(status = True) & Q(population__type_data = 'f') & Q(population__date_register__range=(start_date, end_date)) & Q(population__status_datap = 'ac') & Q(population__aldeia__id = dadosaldeia.id)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++ 
        p1tlsseluk  = DetailFamily.objects.filter(Q(population__gender = 's') & Q(status = True) & Q(population__type_data = 'f') & Q(population__date_register__range=(start_date, end_date)) & Q(population__status_datap = 'ac') & Q(population__aldeia__id = dadosaldeia.id)).count()
      


        #populasaun suku migrasaun tls  mane
        p1tlsmane2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 'm') & Q(population__status_datap = 'ac') & Q(population__aldeia__id = dadosaldeia.id)).count()
        #populasaun suku laran tls Feto
        p1tlsfeto2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 'f') & Q(population__status_datap = 'ac') & Q(population__aldeia__id = dadosaldeia.id)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p1tlsseluk2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, end_date)) & Q(population__gender = 's') & Q(population__status_datap = 'ac') & Q(population__aldeia__id = dadosaldeia.id)).count()
       
        p1tlsmane = p1tlsmane + p1tlsmane2
        p1tlsfeto = p1tlsfeto + p1tlsfeto2
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p1tlsseluk = p1tlsseluk + p1tlsseluk2



        #Quantidade membro Familia
        p1qmembrufamilia = DetailFamily.objects.filter(Q(status = True) & Q(population__status_datap = 'ac') & Q(population__date_register__range=(start_date, end_date)) & Q(population__aldeia__id = dadosaldeia.id)).count()

        if p1qxefefamilia > p1qmembrufamilia :
            p1qmembrufamilia =   p1qxefefamilia - p1qmembrufamilia
        else : 
            p1qmembrufamilia =   p1qmembrufamilia - p1qxefefamilia




        #Quantidade Populasaun
        p1qpopulasaun = DetailFamily.objects.filter(Q(population__status_datap = 'ac') & Q(status = True) & Q(population__date_register__range=(start_date, end_date)) & Q(population__aldeia__id = dadosaldeia.id)).count()




        #Aumenta
        # p3emorisemane = Migration.objects.filter(Q(family_position = 1) & Q(population__status_datap='ac') & Q(population__aldeia__id = dadosaldeia.id)).count()
        #aumenta moris

        #Populasaun Etrangeiro Ne'ebe moris sexu mane temporario
        p3morisemane  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(population__gender = 'm')  & Q(population__aldeia__id = dadosaldeia.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()
        #Populasaun Etrangeiro Ne'ebe moris sexu feto temporario
        p3morisefeto  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(population__gender = 'f')  & Q(population__aldeia__id = dadosaldeia.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3moriseseluk  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(population__gender = 's')  & Q(population__aldeia__id = dadosaldeia.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()
       



       #Populasaun timor Ne'ebe moris sexu mane temporario
        p3morisemanetemp  = Temporary.objects.filter(Q(cidadaunt = 1) & Q(population__gender = 'm')  & Q(population__aldeia__id = dadosaldeia.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()
        #Populasaun timor Ne'ebe moris sexu feto temporario
        p3morisefetotemp  = Temporary.objects.filter(Q(cidadaunt = 1) & Q(population__gender = 'f')  & Q(population__aldeia__id = dadosaldeia.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3moriseseluktemp  = Temporary.objects.filter(Q(cidadaunt = 1) & Q(population__gender = 's')  & Q(population__aldeia__id = dadosaldeia.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='mo')).count()
      


        #Populasaun timor oan ne'ebe muda no  moris sexu mane
        p3moristmane  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 'm')  & Q(population__aldeia__id = dadosaldeia.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
        #Populasaun timor oan ne'ebe muda no  moris sexu feto
        p3moristfeto  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 'f')  & Q(population__aldeia__id = dadosaldeia.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++        
        p3moristseluk  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 's')  & Q(population__aldeia__id = dadosaldeia.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
         #Populasaun timor oan ne'ebe iha suku laran no  moris sexu mane
        


        #Populasaun timor oan ne'ebe iha suku laran no  moris sexu mane
        p3moristmane2  = DetailFamily.objects.filter(Q(population__nationality = '1')  & Q(population__gender = 'm')  & Q(population__aldeia__id = dadosaldeia.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
        #Populasaun timor oan ne'ebe iha suku laran no  moris sexu feto
        p3moristfeto2  = DetailFamily.objects.filter(Q(population__nationality = '1')  & Q(population__gender = 'f')  & Q(population__aldeia__id = dadosaldeia.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
       #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3moristseluk2  = DetailFamily.objects.filter(Q(population__nationality = '1')  & Q(population__gender = 's')  & Q(population__aldeia__id = dadosaldeia.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan)).count()
     



        p3moristmane2 = p3moristmane + p3moristmane2 + p3morisemanetemp
        p3moristfeto2 = p3moristfeto + p3moristfeto2 + p3morisefetotemp
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3moristseluk2 = p3moristseluk + p3moristseluk2 + p3moriseseluktemp



        #muda 
        #muda tama estrangeiro
        p3mudatamaemane  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__gender = 'm')  & Q(population__aldeia__id = dadosaldeia.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()
        p3mudatamaefeto  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__gender = 'f')  & Q(population__aldeia__id = dadosaldeia.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3mudatamaeseluk  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__gender = 's')  & Q(population__aldeia__id = dadosaldeia.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()
       



        p3mudatamatmane  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 'm')  & Q(population__aldeia__id = dadosaldeia.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(from_aldeia__id = dadosaldeia.id).count()
        p3mudatamatfeto  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 'f')  & Q(population__aldeia__id = dadosaldeia.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(from_aldeia__id = dadosaldeia.id).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3mudatamatseluk  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__gender = 's')  & Q(population__aldeia__id = dadosaldeia.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(from_aldeia__id = dadosaldeia.id).count()
    







        #menus mate
        # estrangeiro 
        
        p3mateemane  = Death.objects.filter(Q(population__nationality = '2') & Q(population__gender = 'm') & Q(population__status_datap = 'ma')  &  Q(population__aldeia__id = dadosaldeia.id) & Q(date__year = year) & Q(date__month = fulan)).count()
        p3mateefeto  = Death.objects.filter(Q(population__nationality = '2') & Q(population__gender = 'f') & Q(population__status_datap = 'ma')  &  Q(population__aldeia__id = dadosaldeia.id) & Q(date__year = year) & Q(date__month = fulan)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3mateeseluk  = Death.objects.filter(Q(population__nationality = '2') & Q(population__gender = 's') & Q(population__status_datap = 'ma')  &  Q(population__aldeia__id = dadosaldeia.id) & Q(date__year = year) & Q(date__month = fulan)).count()
    

       
       # timor 
        p3matetmane  = Death.objects.filter(Q(population__nationality = '1') & Q(population__gender = 'm') & Q(population__status_datap = 'ma')  &  Q(population__aldeia__id = dadosaldeia.id) & Q(date__year = year) & Q(date__month = fulan)).count()
        p3matetfeto  = Death.objects.filter(Q(population__nationality = '1') & Q(population__gender = 'f') & Q(population__status_datap = 'ma')  &  Q(population__aldeia__id = dadosaldeia.id) & Q(date__year = year) & Q(date__month = fulan)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3matetseluk  = Death.objects.filter(Q(population__nationality = '1') & Q(population__gender = 's') & Q(population__status_datap = 'ma')  &  Q(population__aldeia__id = dadosaldeia.id) & Q(date__year = year) & Q(date__month = fulan)).count()
       


        #menus muda sai
        #estrageiro

        p3mudasaiemane  = Migrationout.objects.filter(Q(population__nationality = '2') & Q(population__gender = 'm') & Q(population__status_datap = 'mu')   & Q(population__aldeia__id = dadosaldeia.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()
        p3mudasaiefeto  = Migrationout.objects.filter(Q(population__nationality = '2') & Q(population__gender = 'f') & Q(population__status_datap = 'mu')   & Q(population__aldeia__id = dadosaldeia.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3mudasaieseluk  = Migrationout.objects.filter(Q(population__nationality = '2') & Q(population__gender = 's') & Q(population__status_datap = 'mu')   & Q(population__aldeia__id = dadosaldeia.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).count()
       

        p3mudasaitmane  = Migrationout.objects.filter(Q(population__nationality = '1') & Q(population__gender = 'm') & Q(population__status_datap = 'mu')   & Q(population__aldeia__id = dadosaldeia.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(to_aldeia__id = dadosaldeia.id).count()
        p3mudasaitfeto  = Migrationout.objects.filter(Q(population__nationality = '1') & Q(population__gender = 'f') & Q(population__status_datap = 'mu')   & Q(population__aldeia__id = dadosaldeia.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(to_aldeia__id = dadosaldeia.id).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        p3mudasaitseluk  = Migrationout.objects.filter(Q(population__nationality = '1') & Q(population__gender = 's') & Q(population__status_datap = 'mu')   & Q(population__aldeia__id = dadosaldeia.id) & Q(date_migration__year = year) & Q(date_migration__month = fulan)).exclude(to_aldeia__id = dadosaldeia.id).count()
       




        dataagora = end_date_last





    # Total Populasaun Fim do Mes



        # p3morisemane  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(population__gender = 'm')  & Q(population__aldeia__id = dadosaldeia.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='te')).count()


        # #Populasaun Etrangeiro Ne'ebe moris sexu feto temporario
        # p3morisefeto  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(population__gender = 'f')  & Q(population__aldeia__id = dadosaldeia.id) & Q(population__date_of_bird__year = year) & Q(population__date_of_bird__month = fulan) & Q(population__type_data='te')).count()




        #Estranjeiru Mane
        fimestrangeiromane  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 'm') & Q(population__status_datap = 'ac') & Q(population__aldeia__id = dadosaldeia.id)).count()
        #Estranjeiru Feto
        fimestrangeirofeto  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 'f') & Q(population__status_datap = 'ac') & Q(population__aldeia__id = dadosaldeia.id)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        fimestrangeiroseluk  = Migration.objects.filter(Q(cidadaunm = 2) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 's') & Q(population__status_datap = 'ac') & Q(population__aldeia__id = dadosaldeia.id)).count()
       
        # fimestrangeiromane  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(date_arive__range=(start_date, dataagora)) & Q(population__gender = 'm') & Q(population__status_datap = 'te') & Q(population__aldeia__id = dadosaldeia.id)).count()

    
        # fimestrangeirofeto  = Temporary.objects.filter(Q(cidadaunt = 2) & Q(date_arive__range=(start_date, dataagora)) & Q(population__gender = 'f') & Q(population__status_datap = 'te') & Q(population__aldeia__id = dadosaldeia.id)).count()





        #populasaun suku laran Mane 
        fimp1tlsmane  = DetailFamily.objects.filter(Q(population__gender = 'm') & Q(population__date_register__range=(start_date, dataagora))  & Q(status= True) & Q(population__status_datap = 'ac') & Q(population__type_data = 'f') & Q(population__aldeia__id = dadosaldeia.id)).count()
        #populasaun suku laran  Feto
        fimp1tlsfeto  = DetailFamily.objects.filter(Q(population__gender = 'f') & Q(population__type_data = 'f') & Q(population__date_register__range=(start_date, dataagora))  & Q(status = True) & Q(population__status_datap = 'ac') & Q(population__aldeia__id = dadosaldeia.id)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        fimp1tlsseluk  = DetailFamily.objects.filter(Q(population__gender = 's') & Q(population__type_data = 'f') & Q(population__date_register__range=(start_date, dataagora))  & Q(status = True) & Q(population__status_datap = 'ac') & Q(population__aldeia__id = dadosaldeia.id)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
     



        #populasaun suku migrasaun tls  mane
        fimp1tlsmane2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 'm') & Q(population__id_family='i') & Q(population__status_datap = 'ac') & Q(population__aldeia__id = dadosaldeia.id)).count()
        #populasaun suku laran tls Feto
        fimp1tlsfeto2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 'f')  & Q(population__id_family='i') & Q(population__status_datap = 'ac') & Q(population__aldeia__id = dadosaldeia.id)).count()
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        fimp1tlsseluk2  = Migration.objects.filter(Q(cidadaunm = 1) & Q(population__date_register__range=(start_date, dataagora)) & Q(population__gender = 's')  & Q(population__id_family='i') & Q(population__status_datap = 'ac') & Q(population__aldeia__id = dadosaldeia.id)).count()
    

        fimp1tlsmane = fimp1tlsmane + fimp1tlsmane2
        fimp1tlsfeto = fimp1tlsfeto + fimp1tlsfeto2
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++
        fimp1tlsseluk = fimp1tlsseluk + fimp1tlsseluk2



        #Qtd.Xefe Familia
        fimp1qxefefamilia = DetailFamily.objects.filter(Q(family_position = 1) & Q(population__status_datap = 'ac') & Q(population__date_register__range=(start_date, dataagora)) & Q(population__id_family='i') &  Q(population__aldeia__id = dadosaldeia.id)).count()
        
      
      #Quantidade membro Familia
        fimp1qmembrufamilia = DetailFamily.objects.filter(Q(status = True) 
        & Q(population__status_datap = 'ac') & Q(population__id_family='i') & Q(population__date_register__range=(start_date, dataagora)) & Q(population__aldeia__id = dadosaldeia.id)).count()
        fimp1qmembrufamilia = fimp1qmembrufamilia - fimp1qxefefamilia

        #Quantidade Populasaun
        fimp1qpopulasaun = DetailFamily.objects.filter(Q(status = True) 
        & Q(population__status_datap = 'ac') & Q(population__id_family='i') & Q(population__date_register__range=(start_date, dataagora)) & Q(population__aldeia__id = dadosaldeia.id)).count()






        family_member.append({
     
            'aldeia' : dadosaldeia.name,
            'p1qxefefamilia' : p1qxefefamilia,
                     #Populasaun Estrangeiru
           #Populasaun Estrangeiru
            'p1estrangeiromane' : p1estrangeiromane,
            'p1estrangeirofeto' : p1estrangeirofeto,
            'p1estrangeiroseluk' : p1estrangeiroseluk,

            #populasaun Suku
            'p1tlsmane' : p1tlsmane,
            'p1tlsfeto' : p1tlsfeto,
            'p1tlsseluk' : p1tlsseluk,


            'p1qmembrufamilia' : p1qmembrufamilia,
            'p1qpopulasaun' : p1qpopulasaun,

            #aumenta
            #Aumenta Moris
            #aumenta moris estrangiro mane,feto
            'p3morisemane' : p3morisemane,
            'p3morisefeto' : p3morisefeto,
            'p3moriseseluk' : p3moriseseluk,

            
            #aumenta moris Timor oan mane,feto
            'p3moristmane2' : p3moristmane2,
            'p3moristfeto2' : p3moristfeto2,
            'p3moristseluk2' : p3moristseluk2,
            



            #aumenta muda tama
            #muda tama estrageiro
            'p3mudatamaemane' : p3mudatamaemane,
            'p3mudatamaefeto' : p3mudatamaefeto,
            'p3mudatamaeseluk' : p3mudatamaeseluk,


            'p3mudatamatfeto' : p3mudatamatfeto,
            'p3mudatamatmane' : p3mudatamatmane,
            'p3mudatamatseluk' : p3mudatamatseluk,

            #menus 
            #menus mate 
            'p3mateemane' : p3mateemane,
            'p3mateefeto' : p3mateefeto,
            'p3mateeseluk' : p3mateeseluk,

            'p3matetmane' : p3matetmane,
            'p3matetfeto' : p3matetfeto,
            'p3matetseluk' : p3matetseluk,

            #menus muda sai
            'p3mudasaiefeto' : p3mudasaiefeto,
            'p3mudasaiemane' : p3mudasaiemane,
            'p3mudasaieseluk' : p3mudasaieseluk,

            'p3mudasaitfeto' : p3mudasaitfeto,
            'p3mudasaitmane' : p3mudasaitmane,
            'p3mudasaitseluk' : p3mudasaieseluk,


            #fim do mes
            #estrangeiro

            'fimestrangeiromane' : fimestrangeiromane,
            'fimestrangeirofeto' : fimestrangeirofeto,
            'fimestrangeiroseluk' : fimestrangeirofeto,

            'fimp1tlsmane' : fimp1tlsmane,
            'fimp1tlsfeto' : fimp1tlsfeto,
            'fimp1tlsseluk' : fimp1tlsseluk,

            'fimp1qxefefamilia' : fimp1qxefefamilia,
            'fimp1qmembrufamilia' : fimp1qmembrufamilia,
            'fimp1qpopulasaun' : fimp1qpopulasaun,






            })
  
    template = "population_report/b4/reportjeralsuku-b4-print.html"
    context = {
        'title' : 'Relatorio Dados Rekapitulasaun Populasaun',
        'family_member' : family_member,
        'year' : year,
        'munisipiu_title' : munisipiu_title,
        'postu_title' : postu_title,
        'suku_title' : suku_title,
        'fulan' : fulan,

    } 

    return render(request,template, context)