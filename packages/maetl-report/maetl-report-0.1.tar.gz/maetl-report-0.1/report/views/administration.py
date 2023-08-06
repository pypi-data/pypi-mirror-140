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
from administration.models import *
# ===============================
@login_required
def nationalReportDashboard(request):
	all_municipality = Municipality.objects.all()
	currentYear = date.today().year
	all_year = Year.objects.all()
	municipality = Municipality.objects.all()
	allReport = []
	for i in municipality:
		decisionKonselluSuku = Decision.objects.filter(decision_type="Konsellu Suku",municipality__id=i.id).count()
		decisionXefeSuku = Decision.objects.filter(decision_type="Xefe Suku",municipality__id=i.id).count()
		inventory = Inventory.objects.filter(municipality__id=i.id).count()
		letterOut = LetterOut.objects.filter(municipality__id=i.id).count()
		letterIn = LetterIn.objects.filter(municipality__id=i.id).count()
		expedition = LetterOutExpedition.objects.filter(municipality__id=i.id).count()
		communityLeadership = CommunityLeadership.objects.filter(municipality__id=i.id).count()
		complaint = Complaint.objects.filter(municipality__id=i.id).count()
		visitor = Visitor.objects.filter(municipality__id=i.id).count()
		allReport.append({
			"municipalityID":i.hckey,
			"municipality":i.name,
			"a1":decisionKonselluSuku,
			"a2":decisionXefeSuku,
			"a3":inventory,
			"a4":letterOut,
			"a5":letterIn,
			"a6":expedition,
			"a7":communityLeadership,
			"a10":complaint,
			"a11":visitor,
			})

	context = {
		'title': "Relatóriu Livru Administrasaun",
		'currentYear': currentYear,
		'all_year':all_year,
		'allReport':allReport,
		'municipality': all_municipality
	}
	return render(request, 'administration/dashboard.html', context)

def getMunicipalityLabel(municipality):
	if municipality == "Baucau" or municipality=="Bobonaro" or municipality=="Dili" or municipality=="Ermera":
		return  str("Autoridade Munisipal : ")+str(municipality)
	elif municipality == "Oe-cusse":
		return str("Rejiaun Autonomu : RAEOA ")
	else:
		return str("Munisipiu : ")+str(municipality)

def getPostLabel(post):
	return str("Postu Administrativu : ")+str(post)

def getVillageLabel(post):
	return str("Suku : ")+str(post)

@login_required
def nationalReportFilter(request):
	if request.method == "POST":
		administrationReport = request.POST.get('administrationReport')
		year = request.POST.get('year')
		year = get_object_or_404(Year,year=year)
		municipality = request.POST.get('municipality')
		administrativepost = request.POST.get('administrativepost')
		village = request.POST.get('village')
		if administrationReport == "A1":
			decision_type = "Konsellu Suku"
			if municipality != "" and administrativepost == "" and village == "":
				municipality = get_object_or_404(Municipality,id=municipality)
				# report municipality
				decisionlist = Decision.objects.filter(year=year,decision_type=decision_type,municipality=municipality)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":administrativepost,"village":village,\
					'page1':"NationalReport",'year':year,'decision_type':decision_type,'decisionlist':decisionlist,"title":"Desizaun Konsellu Suku"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A1_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A1_report.html",data)
			elif administrativepost != "" and village == "":
				municipality = get_object_or_404(Municipality,id=municipality)
				administrativepost = get_object_or_404(AdministrativePost,id=administrativepost)
				# report administrativepost
				decisionlist = Decision.objects.filter(year=year,decision_type=decision_type,municipality=municipality,administrativepost=administrativepost)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":getPostLabel(administrativepost.name),"village":village,\
				'page1':"NationalReport",'year':year,'decision_type':decision_type,'decisionlist':decisionlist,"title":"Desizaun Konsellu Suku"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A1_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A1_report.html",data)
			elif village != "":
				municipality = get_object_or_404(Municipality,id=municipality)
				administrativepost = get_object_or_404(AdministrativePost,id=administrativepost)
				village = get_object_or_404(Village,id=village)
				# report administrativepost
				decisionlist = Decision.objects.filter(year=year,decision_type=decision_type,municipality=municipality,administrativepost=administrativepost,village=village)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":getPostLabel(administrativepost.name),"village":getVillageLabel(village.name),\
				'page1':"NationalReport",'year':year,'decision_type':decision_type,'decisionlist':decisionlist,"title":"Desizaun Konsellu Suku"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A1_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A1_report.html",data)
			else:
				decisionlist = Decision.objects.filter(year=year,decision_type=decision_type)
				data ={"municipality":municipality,"administrativepost":administrativepost,"village":village,\
				'page1':"NationalReport",'year':year,'decision_type':decision_type,'decisionlist':decisionlist,"title":"Desizaun Konsellu Suku"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A1_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A1_report.html",data)
		if administrationReport == "A2":
			decision_type = "Xefe Suku"
			if municipality != "" and administrativepost == "" and village == "":
				# report municipality
				municipality = get_object_or_404(Municipality,id=municipality)
				decisionlist = Decision.objects.filter(year=year,decision_type=decision_type,municipality=municipality)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":administrativepost,"village":village,\
					'page1':"NationalReport",'year':year,'decision_type':decision_type,'decisionlist':decisionlist,"title":"Desizaun Xefe Suku"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A2_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A2_report.html",data)
			elif administrativepost != "" and village == "":
				municipality = get_object_or_404(Municipality,id=municipality)
				administrativepost = get_object_or_404(AdministrativePost,id=administrativepost)
				# report administrativepost
				decisionlist = Decision.objects.filter(year=year,decision_type=decision_type,municipality=municipality,administrativepost=administrativepost)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":getPostLabel(administrativepost.name),"village":village,\
				'page1':"NationalReport",'year':year,'decision_type':decision_type,'decisionlist':decisionlist,"title":"Desizaun Xefe Suku"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A2_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A2_report.html",data)
			elif village != "":
				municipality = get_object_or_404(Municipality,id=municipality)
				administrativepost = get_object_or_404(AdministrativePost,id=administrativepost)
				village = get_object_or_404(Village,id=village)
				# report administrativepost
				decisionlist = Decision.objects.filter(year=year,decision_type=decision_type,municipality=municipality,administrativepost=administrativepost,village=village)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":getPostLabel(administrativepost.name),"village":getVillageLabel(village.name),\
				'page1':"NationalReport",'year':year,'decision_type':decision_type,'decisionlist':decisionlist,"title":"Desizaun Xefe Suku"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A2_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A2_report.html",data)
			else:
				decisionlist = Decision.objects.filter(year=year,decision_type=decision_type)
				data ={"municipality":municipality,"administrativepost":administrativepost,"village":village,\
				'page1':"NationalReport",'year':year,'decision_type':decision_type,'decisionlist':decisionlist,"title":"Desizaun Xefe Suku"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A2_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A2_report.html",data)
		
		if administrationReport == "A3":
			if municipality != "" and administrativepost == "" and village == "":
				# report municipality
				municipality = get_object_or_404(Municipality,id=municipality)
				inventoryList = UsedInventoryDetail.objects.filter(inventory__year=year,municipality=municipality)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":administrativepost,"village":village,\
					'page1':"NationalReport",'year':year,'inventoryList':inventoryList,"title":"Livru Inventariu"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A3_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A3_report.html",data)
			elif administrativepost != "" and village == "":
				municipality = get_object_or_404(Municipality,id=municipality)
				administrativepost = get_object_or_404(AdministrativePost,id=administrativepost)
				# report administrativepost
				inventoryList = UsedInventoryDetail.objects.filter(inventory__year=year,municipality=municipality,administrativepost=administrativepost)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":getPostLabel(administrativepost.name),"village":village,\
					'page1':"NationalReport",'year':year,'inventoryList':inventoryList,"title":"Livru Inventariu"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A3_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A3_report.html",data)
			elif village != "":
				municipality = get_object_or_404(Municipality,id=municipality)
				administrativepost = get_object_or_404(AdministrativePost,id=administrativepost)
				village = get_object_or_404(Village,id=village)
				# report administrativepost
				inventoryList = UsedInventoryDetail.objects.filter(inventory__year=year,municipality=municipality,administrativepost=administrativepost,village=village)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":getPostLabel(administrativepost.name),"village":getVillageLabel(village.name),\
					'page1':"NationalReport",'year':year,'inventoryList':inventoryList,"title":"Livru Inventariu"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A3_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A3_report.html",data)
			else:
				inventoryList = UsedInventoryDetail.objects.filter(inventory__year=year)
				data ={"municipality":municipality,"administrativepost":administrativepost,"village":village,\
					'page1':"NationalReport",'year':year,'inventoryList':inventoryList,"title":"Livru Inventariu"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A3_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A3_report.html",data)
		
		if administrationReport == "A4":
			if municipality != "" and administrativepost == "" and village == "":
				# report municipality
				municipality = get_object_or_404(Municipality,id=municipality)
				letterOutList = LetterOut.objects.filter(year=year,municipality=municipality)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":administrativepost,"village":village,\
					'page1':"NationalReport",'year':year,'letterOutList':letterOutList,"title":"Livru Surat Sai"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A4_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A4_report.html",data)
			elif administrativepost != "" and village == "":
				municipality = get_object_or_404(Municipality,id=municipality)
				administrativepost = get_object_or_404(AdministrativePost,id=administrativepost)
				# report administrativepost
				letterOutList = LetterOut.objects.filter(year=year,municipality=municipality,administrativepost=administrativepost)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":getPostLabel(administrativepost.name),"village":village,\
					'page1':"NationalReport",'year':year,'letterOutList':letterOutList,"title":"Livru Surat Sai"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A4_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A4_report.html",data)
			elif village != "":
				municipality = get_object_or_404(Municipality,id=municipality)
				administrativepost = get_object_or_404(AdministrativePost,id=administrativepost)
				village = get_object_or_404(Village,id=village)
				# report administrativepost
				letterOutList = LetterOut.objects.filter(year=year,municipality=municipality,administrativepost=administrativepost,village=village)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":getPostLabel(administrativepost.name),"village":getVillageLabel(village.name),\
					'page1':"NationalReport",'year':year,'letterOutList':letterOutList,"title":"Livru Surat Sai"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A4_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A4_report.html",data)
			else:
				letterOutList = LetterOut.objects.filter(year=year)
				data ={"municipality":municipality,"administrativepost":administrativepost,"village":village,\
					'page1':"NationalReport",'year':year,'letterOutList':letterOutList,"title":"Livru Surat Sai"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A4_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A4_report.html",data)

		if administrationReport == "A5":
			if municipality != "" and administrativepost == "" and village == "":
				# report municipality
				municipality = get_object_or_404(Municipality,id=municipality)
				letterInList = LetterIn.objects.filter(year=year,municipality=municipality)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":administrativepost,"village":village,\
					'page1':"NationalReport",'year':year,'letterInList':letterInList,"title":"Livru Surat Tama"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A5_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A5_report.html",data)
			elif administrativepost != "" and village == "":
				municipality = get_object_or_404(Municipality,id=municipality)
				administrativepost = get_object_or_404(AdministrativePost,id=administrativepost)
				# report administrativepost
				letterInList = LetterIn.objects.filter(year=year,municipality=municipality,administrativepost=administrativepost)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":getPostLabel(administrativepost.name),"village":village,\
					'page1':"NationalReport",'year':year,'letterInList':letterInList,"title":"Livru Surat Tama"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A5_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A5_report.html",data)
			elif village != "":
				municipality = get_object_or_404(Municipality,id=municipality)
				administrativepost = get_object_or_404(AdministrativePost,id=administrativepost)
				village = get_object_or_404(Village,id=village)
				# report administrativepost
				letterInList = LetterIn.objects.filter(year=year,municipality=municipality,administrativepost=administrativepost,village=village)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":getPostLabel(administrativepost.name),"village":getVillageLabel(village.name),\
					'page1':"NationalReport",'year':year,'letterInList':letterInList,"title":"Livru Surat Tama"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A5_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A5_report.html",data)
			else:
				letterInList = LetterIn.objects.filter(year=year)
				data ={"municipality":municipality,"administrativepost":administrativepost,"village":village,\
					'page1':"NationalReport",'year':year,'letterInList':letterInList,"title":"Livru Surat Tama"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A5_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A5_report.html",data)
		
		if administrationReport == "A6":
			if municipality != "" and administrativepost == "" and village == "":
				# report municipality
				municipality = get_object_or_404(Municipality,id=municipality)
				expeditionList = LetterOutExpedition.objects.filter(letter_out__year=year,municipality=municipality)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":administrativepost,"village":village,\
					'page1':"NationalReport",'year':year,'expeditionList':expeditionList,"title":"Livru Espedisaun"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A6_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A6_report.html",data)
			elif administrativepost != "" and village == "":
				municipality = get_object_or_404(Municipality,id=municipality)
				administrativepost = get_object_or_404(AdministrativePost,id=administrativepost)
				# report administrativepost
				expeditionList = LetterOutExpedition.objects.filter(letter_out__year=year,municipality=municipality,administrativepost=administrativepost)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":getPostLabel(administrativepost.name),"village":village,\
					'page1':"NationalReport",'year':year,'expeditionList':expeditionList,"title":"Livru Espedisaun"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A6_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A6_report.html",data)
			elif village != "":
				municipality = get_object_or_404(Municipality,id=municipality)
				administrativepost = get_object_or_404(AdministrativePost,id=administrativepost)
				village = get_object_or_404(Village,id=village)
				# report administrativepost
				expeditionList = LetterOutExpedition.objects.filter(letter_out__year=year,municipality=municipality,administrativepost=administrativepost,village=village)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":getPostLabel(administrativepost.name),"village":getVillageLabel(village.name),\
					'page1':"NationalReport",'year':year,'expeditionList':expeditionList,"title":"Livru Espedisaun"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A6_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A6_report.html",data)
			else:
				expeditionList = LetterOutExpedition.objects.filter(letter_out__year=year)
				data ={"municipality":municipality,"administrativepost":administrativepost,"village":village,\
					'page1':"NationalReport",'year':year,'expeditionList':expeditionList,"title":"Livru Espedisaun"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A6_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A6_report.html",data)

		if administrationReport == "A7":
			if municipality != "" and administrativepost == "" and village == "":
				# report municipality
				municipality = get_object_or_404(Municipality,id=municipality)
				commLeadershipList = CommunityLeadership.objects.filter(year=year,status="Yes",municipality=municipality)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":administrativepost,"village":village,\
					'page1':"NationalReport",'year':year,'commLeadershipList':commLeadershipList,"title":"Livru Rejistu Lideransa Komunitaria"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A7_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A7_report.html",data)
			elif administrativepost != "" and village == "":
				municipality = get_object_or_404(Municipality,id=municipality)
				administrativepost = get_object_or_404(AdministrativePost,id=administrativepost)
				# report administrativepost
				commLeadershipList = CommunityLeadership.objects.filter(year=year,status="Yes",municipality=municipality,administrativepost=administrativepost)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":getPostLabel(administrativepost.name),"village":village,\
					'page1':"NationalReport",'year':year,'commLeadershipList':commLeadershipList,"title":"Livru Rejistu Lideransa Komunitaria"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A7_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A7_report.html",data)
			elif village != "":
				municipality = get_object_or_404(Municipality,id=municipality)
				administrativepost = get_object_or_404(AdministrativePost,id=administrativepost)
				village = get_object_or_404(Village,id=village)
				# report administrativepost
				commLeadershipList = CommunityLeadership.objects.filter(year=year,status="Yes",municipality=municipality,administrativepost=administrativepost,village=village)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":getPostLabel(administrativepost.name),"village":getVillageLabel(village.name),\
					'page1':"NationalReport",'year':year,'commLeadershipList':commLeadershipList,"title":"Livru Rejistu Lideransa Komunitaria"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A7_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A7_report.html",data)
			else:
				commLeadershipList = CommunityLeadership.objects.filter(year=year,status="Yes")
				data ={"municipality":municipality,"administrativepost":administrativepost,"village":village,\
					'page1':"NationalReport",'year':year,'commLeadershipList':commLeadershipList,"title":"Livru Rejistu Lideransa Komunitaria"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A7_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A7_report.html",data)

		if administrationReport == "A10":
			if municipality != "" and administrativepost == "" and village == "":
				# report municipality
				municipality = get_object_or_404(Municipality,id=municipality)
				ComplaintList = Complaint.objects.filter(year=year,municipality=municipality)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":administrativepost,"village":village,\
					'page1':"NationalReport",'year':year,'ComplaintList':ComplaintList,"title":"Livru Rejistu Keixa"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A10_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A10_report.html",data)
			elif administrativepost != "" and village == "":
				municipality = get_object_or_404(Municipality,id=municipality)
				administrativepost = get_object_or_404(AdministrativePost,id=administrativepost)
				# report administrativepost
				ComplaintList = Complaint.objects.filter(year=year,municipality=municipality,administrativepost=administrativepost)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":getPostLabel(administrativepost.name),"village":village,\
					'page1':"NationalReport",'year':year,'ComplaintList':ComplaintList,"title":"Livru Rejistu Keixa"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A10_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A10_report.html",data)
			elif village != "":
				municipality = get_object_or_404(Municipality,id=municipality)
				administrativepost = get_object_or_404(AdministrativePost,id=administrativepost)
				village = get_object_or_404(Village,id=village)
				# report administrativepost
				ComplaintList = Complaint.objects.filter(year=year,municipality=municipality,administrativepost=administrativepost,village=village)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":getPostLabel(administrativepost.name),"village":getVillageLabel(village.name),\
					'page1':"NationalReport",'year':year,'ComplaintList':ComplaintList,"title":"Livru Rejistu Keixa"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A10_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A10_report.html",data)
			else:
				ComplaintList = Complaint.objects.filter(year=year)
				data ={"municipality":municipality,"administrativepost":administrativepost,"village":village,\
					'page1':"NationalReport",'year':year,'ComplaintList':ComplaintList,"title":"Livru Rejistu Keixa"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A10_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A10_report.html",data)

		if administrationReport == "A11":
			if municipality != "" and administrativepost == "" and village == "":
				# report municipality
				municipality = get_object_or_404(Municipality,id=municipality)
				VisitorList = Visitor.objects.filter(year=year,municipality=municipality)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":administrativepost,"village":village,\
					'page1':"NationalReport",'year':year,'VisitorList':VisitorList,"title":"Livru Rejistu Bainaka"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A11_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A11_report.html",data)
			elif administrativepost != "" and village == "":
				municipality = get_object_or_404(Municipality,id=municipality)
				administrativepost = get_object_or_404(AdministrativePost,id=administrativepost)
				# report administrativepost
				VisitorList = Visitor.objects.filter(year=year,municipality=municipality,administrativepost=administrativepost)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":getPostLabel(administrativepost.name),"village":village,\
					'page1':"NationalReport",'year':year,'VisitorList':VisitorList,"title":"Livru Rejistu Bainaka"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A11_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A11_report.html",data)
			elif village != "":
				municipality = get_object_or_404(Municipality,id=municipality)
				administrativepost = get_object_or_404(AdministrativePost,id=administrativepost)
				village = get_object_or_404(Village,id=village)
				# report administrativepost
				VisitorList = Visitor.objects.filter(year=year,municipality=municipality,administrativepost=administrativepost,village=village)
				data ={"municipality":getMunicipalityLabel(municipality.name),"administrativepost":getPostLabel(administrativepost.name),"village":getVillageLabel(village.name),\
					'page1':"NationalReport",'year':year,'VisitorList':VisitorList,"title":"Livru Rejistu Bainaka"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A11_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A11_report.html",data)
			else:
				VisitorList = Visitor.objects.filter(year=year)
				data ={"municipality":municipality,"administrativepost":administrativepost,"village":village,\
					'page1':"NationalReport",'year':year,'VisitorList':VisitorList,"title":"Livru Rejistu Bainaka"}
				if 'print' in request.POST:
					data["page"] = "print"
					return render(request,"administration_layout/report/A11_report.html",data)
				if 'excel' in request.POST:
					data["page"] = "excel"
					return render(request,"administration_layout/report/A11_report.html",data)

@login_required
def A1Munisipiu(request,Munid):
	municipality = get_object_or_404(Municipality,hckey=Munid)
	a1 = Decision.objects.filter(municipality=municipality,decision_type="Konsellu Suku").order_by('administrativepost','-meeting_date')
	context = {
		'title': f"Relatóriu Livru Administrasaun A1 Munisípiu {municipality.name}",
		'municipality': municipality,
		'listA1': a1,
	}
	return render(request, 'administration/A1.html', context)

@login_required
def PrintA1Munisipiu(request,Munid):
	municipality = get_object_or_404(Municipality,hckey=Munid)
	a1 = Decision.objects.filter(municipality=municipality,decision_type="Konsellu Suku").order_by('administrativepost','-meeting_date')
	context = {
		'title': f"Relatóriu Livru Administrasaun A1 Munisípiu {municipality.name}",
		'municipality': municipality,
		'listA1': a1,
	}
	return render(request, 'administration/PrintA1.html', context)

@login_required
def A2Munisipiu(request,Munid):
	municipality = get_object_or_404(Municipality,hckey=Munid)
	a2 = Decision.objects.filter(municipality=municipality,decision_type="Xefe Suku").order_by('administrativepost','-meeting_date')
	context = {
		'title': f"Relatóriu Livru Administrasaun A2 Munisípiu {municipality.name}",
		'municipality': municipality,
		'listA2': a2,
	}
	return render(request, 'administration/A2.html', context)

@login_required
def PrintA2Munisipiu(request,Munid):
	municipality = get_object_or_404(Municipality,hckey=Munid)
	a2 = Decision.objects.filter(municipality=municipality,decision_type="Xefe Suku").order_by('administrativepost','-meeting_date')
	context = {
		'title': f"Relatóriu Livru Administrasaun A2 Munisípiu {municipality.name}",
		'municipality': municipality,
		'listA2': a2,
	}
	return render(request, 'administration/PrintA2.html', context)

@login_required
def A3Munisipiu(request,Munid):
	municipality = get_object_or_404(Municipality,hckey=Munid)
	inventoryList = UsedInventoryDetail.objects.filter(municipality=municipality).order_by('administrativepost','-inventory__recieve_date')
	context = {
		'title': f"Relatóriu Livru Administrasaun A3 Munisípiu {municipality.name}",
		'municipality': municipality,
		'listA3': inventoryList,
	}
	return render(request, 'administration/A3.html', context)

@login_required
def PrintA3Munisipiu(request,Munid):
	municipality = get_object_or_404(Municipality,hckey=Munid)
	inventoryList = UsedInventoryDetail.objects.filter(municipality=municipality).order_by('administrativepost','-inventory__recieve_date')
	context = {
		'title': f"Relatóriu Livru Administrasaun A3 Munisípiu {municipality.name}",
		'municipality': municipality,
		'listA3': inventoryList,
	}
	return render(request, 'administration/PrintA3.html', context)

@login_required
def A4Munisipiu(request,Munid):
	municipality = get_object_or_404(Municipality,hckey=Munid)
	letterOutList = LetterOut.objects.filter(municipality=municipality).order_by('administrativepost','-letter_date')
	context = {
		'title': f"Relatóriu Livru Administrasaun A4 Munisípiu {municipality.name}",
		'municipality': municipality,
		'listA4': letterOutList,
	}
	return render(request, 'administration/A4.html', context)

@login_required
def PrintA4Munisipiu(request,Munid):
	municipality = get_object_or_404(Municipality,hckey=Munid)
	letterOutList = LetterOut.objects.filter(municipality=municipality).order_by('administrativepost','-letter_date')
	context = {
		'title': f"Relatóriu Livru Administrasaun A4 Munisípiu {municipality.name}",
		'municipality': municipality,
		'listA4': letterOutList,
	}
	return render(request, 'administration/PrintA4.html', context)

@login_required
def A5Munisipiu(request,Munid):
	municipality = get_object_or_404(Municipality,hckey=Munid)
	letterInList = LetterIn.objects.filter(municipality=municipality).order_by('administrativepost','-letter_date')
	context = {
		'title': f"Relatóriu Livru Administrasaun A5 Munisípiu {municipality.name}",
		'municipality': municipality,
		'listA5': letterInList,
	}
	return render(request, 'administration/A5.html', context)

@login_required
def PrintA5Munisipiu(request,Munid):
	municipality = get_object_or_404(Municipality,hckey=Munid)
	letterInList = LetterIn.objects.filter(municipality=municipality).order_by('administrativepost','-letter_date')
	context = {
		'title': f"Relatóriu Livru Administrasaun A5 Munisípiu {municipality.name}",
		'municipality': municipality,
		'listA5': letterInList,
	}
	return render(request, 'administration/PrintA5.html', context)

@login_required
def A6Munisipiu(request,Munid):
	municipality = get_object_or_404(Municipality,hckey=Munid)
	expeditionList = LetterOutExpedition.objects.filter(municipality=municipality).order_by('administrativepost','-letter_out__letter_date')
	context = {
		'title': f"Relatóriu Livru Administrasaun A6 Munisípiu {municipality.name}",
		'municipality': municipality,
		'listA6': expeditionList,
	}
	return render(request, 'administration/A6.html', context)

@login_required
def PrintA6Munisipiu(request,Munid):
	municipality = get_object_or_404(Municipality,hckey=Munid)
	expeditionList = LetterOutExpedition.objects.filter(municipality=municipality).order_by('administrativepost','-letter_out__letter_date')
	context = {
		'title': f"Relatóriu Livru Administrasaun A6 Munisípiu {municipality.name}",
		'municipality': municipality,
		'listA6': expeditionList,
	}
	return render(request, 'administration/PrintA6.html', context)

@login_required
def A7Munisipiu(request,Munid):
	municipality = get_object_or_404(Municipality,hckey=Munid)
	commLeadershipList = CommunityLeadership.objects.filter(status="Yes",municipality=municipality).order_by('administrativepost','position__id')
	context = {
		'title': f"Relatóriu Livru Administrasaun A7 Munisípiu {municipality.name}",
		'municipality': municipality,
		'listA7': commLeadershipList,
	}
	return render(request, 'administration/A7.html', context)

@login_required
def PrintA7Munisipiu(request,Munid):
	municipality = get_object_or_404(Municipality,hckey=Munid)
	commLeadershipList = CommunityLeadership.objects.filter(status="Yes",municipality=municipality).order_by('administrativepost','position__id')
	context = {
		'title': f"Relatóriu Livru Administrasaun A7 Munisípiu {municipality.name}",
		'municipality': municipality,
		'listA7': commLeadershipList,
	}
	return render(request, 'administration/PrintA7.html', context)

@login_required
def A10Munisipiu(request,Munid):
	municipality = get_object_or_404(Municipality,hckey=Munid)
	ComplaintList = Complaint.objects.filter(municipality=municipality).order_by('administrativepost','-date')
	context = {
		'title': f"Relatóriu Livru Administrasaun A10 Munisípiu {municipality.name}",
		'municipality': municipality,
		'listA10': ComplaintList,
	}
	return render(request, 'administration/A10.html', context)

@login_required
def PrintA10Munisipiu(request,Munid):
	municipality = get_object_or_404(Municipality,hckey=Munid)
	ComplaintList = Complaint.objects.filter(municipality=municipality).order_by('administrativepost','-date')
	context = {
		'title': f"Relatóriu Livru Administrasaun A10 Munisípiu {municipality.name}",
		'municipality': municipality,
		'listA10': ComplaintList,
	}
	return render(request, 'administration/PrintA10.html', context)

@login_required
def A11Munisipiu(request,Munid):
	municipality = get_object_or_404(Municipality,hckey=Munid)
	visitorList = Visitor.objects.filter(municipality=municipality).order_by('administrativepost','-visitDate')
	context = {
		'title': f"Relatóriu Livru Administrasaun A11 Munisípiu {municipality.name}",
		'municipality': municipality,
		'listA11': visitorList,
	}
	return render(request, 'administration/A11.html', context)

@login_required
def PrintA11Munisipiu(request,Munid):
	municipality = get_object_or_404(Municipality,hckey=Munid)
	visitorList = Visitor.objects.filter(municipality=municipality).order_by('administrativepost','-visitDate')
	context = {
		'title': f"Relatóriu Livru Administrasaun A11 Munisípiu {municipality.name}",
		'municipality': municipality,
		'listA11': visitorList,
	}
	return render(request, 'administration/PrintA11.html', context)








