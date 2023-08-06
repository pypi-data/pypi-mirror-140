	
from django.shortcuts import render,redirect, get_object_or_404,HttpResponse
from django.contrib import messages
from ..forms import *
from ..models import *
from employee.models import *
from django.contrib.auth.models import User,Group
from custom.utils import *
# pdf library
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from main.decorators import *
from django.contrib.auth.decorators import login_required
import datetime
from employee.utils import *
from django.contrib.auth.hashers import make_password

# Create your views here.
@login_required
def communityLeadershipList(request):
	group = request.user.groups.all()[0].name
	if group == "admin":
		communityLeadershipList = CommunityLeadership.objects.filter(status="Yes").order_by('village__id')
	else:
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		communityLeadershipList = CommunityLeadership.objects.filter(status="Yes",village=userAddress.employee.village).order_by('position__id')
	context = {
		"group":group,
		"title":"Lideransa Komunitária",
		'commLeaderActive':"active",
		'communityLeadershipList':communityLeadershipList,
	}
	return render(request, 'administration_layout/layout/communityLeadership.html',context)

@login_required
def periodList(request):
	group = request.user.groups.all()[0].name
	if group == "admin":
		period = MandatePeriod.objects.all().order_by('status')
	else:
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		period = MandatePeriod.objects.all().order_by('status')
	context = {
		"group":group,
		"title":"Periodu Mandatu",
		'periodActive':"active",
		'page':"list",
		'period':period,
	}
	return render(request, 'administration_layout/layout/period.html',context)

@login_required
def detailPeriod(request,hashid):
	group = request.user.groups.all()[0].name
	periodData = get_object_or_404(MandatePeriod,id=hashid)
	communityLeadershipList = CommunityLeadership.objects.filter(period=periodData,status="No").order_by('-id')
	period = str(periodData.start)+str("-")+str(periodData.end)
	context = {
		"group":group,
		"title":f"Lideransa Komunitária Periodu {period}",
		'periodActive':"active",
		'page':"history",
		'periodData':periodData,
		'communityLeadershipList':communityLeadershipList,
	}
	return render(request, 'administration_layout/layout/period.html',context)

@login_required
@allowed_users(allowed_roles=['admin'])
def addPeriod(request):
	group = request.user.groups.all()[0].name
	if request.method == "POST":
		newid,_ = getnewid(MandatePeriod)
		hashid = hash_md5(str(newid))
		form = PeriodForm(request.POST)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.id = newid
			instance.user_created = get_object_or_404(User,id=request.user.id)
			instance.hashed = hashid
			instance.save()
			messages.success(request, f'Periodu Foun Adisiona ho Susesu.')
			return redirect('administration:periodList')
	else:
		form = PeriodForm()
	context = {
		"group":group,
		"title":"Adisiona Mandatu Periodu",
		'periodActive':"active",
		'page':'form',
		'form':form,
	}
	return render(request, 'administration_layout/layout/period.html',context)

@login_required
@allowed_users(allowed_roles=['admin'])
def updatePeriod(request,hashid):
	group = request.user.groups.all()[0].name
	period = get_object_or_404(MandatePeriod,id=hashid)
	if request.method == "POST":
		form = PeriodForm(request.POST,instance=period)
		if form.is_valid():
			form.save()
			messages.success(request, f'Dadus Periodu Altera ho Susesu.')
			return redirect('administration:periodList')
	else:
		form = PeriodForm(instance=period)
	context = {
		"group":group,
		"title":"Altera Mandatu Periodu",
		'periodActive':"active",
		'page':'form',
		'form':form,
	}
	return render(request, 'administration_layout/layout/period.html',context)

@login_required
@allowed_users(allowed_roles=['admin','xefe'])
def load_aldeia(request):
	village_id = request.GET.get('village')
	aldeia = Aldeia.objects.filter(village__id=village_id).order_by('name')
	return render(request, 'administration_layout/layout/aldeia_dropdown.html', {'aldeia': aldeia})

@login_required
@allowed_users(allowed_roles=['admin','xefe'])
def load_populations(request):
	aldeia_id = request.GET.get('aldeia')
	leader = CommunityLeadership.objects.filter(position__in=(Position.objects.all()),status="Yes").values_list('population__id',flat=True)
	populations = Population.objects.filter(aldeia__id=aldeia_id,status_datap='ac',type_data='f').order_by('name').exclude(id__in=leader)
	return render(request, 'administration_layout/layout/population_dropdown.html', {'populations': populations})

@login_required
@allowed_users(allowed_roles=['admin','xefe'])
def addCommunityLidership(request):
	group = request.user.groups.all()[0].name
	municipality = Municipality.objects.all()
	userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
	if request.method == "POST":
		newid,_ = getnewid(CommunityLeadership)
		hashid = hash_md5(str(newid))
		form = CommunityLeadershipForm(request.POST,user=userAddress)
		
		if form.is_valid():
			instance = form.save(commit=False)
			instance.id = newid
			user = get_object_or_404(User,id=request.user.id)
			instance.user_created = user
			municipality = get_object_or_404(Municipality,id=userAddress.employee.municipality.id)
			administrativepost = get_object_or_404(AdministrativePost,id=userAddress.employee.administrativepost.id)
			village = get_object_or_404(Village,id=userAddress.employee.village.id)
			instance.municipality = municipality
			instance.administrativepost = administrativepost
			instance.village = village
			instance.hashed = hashid
			instance.status = "Yes"
			instance.save()
			messages.success(request, f'Lideransa Komunitária Foun Adisiona ho Susesu.')
			return redirect('administration:communityLeadershipList')
	else:
		form = CommunityLeadershipForm(user=userAddress)
	context = {
		"group":group,
		"title":"Adisiona Lideransa Komunitária",
		'commLeaderActive':"active",
		'page':"form",
		'municipality':municipality,
		'form':form,
	}
	return render(request, 'administration_layout/layout/communityLeadershipForm.html',context)

@login_required
@allowed_users(allowed_roles=['xefe'])
def addCommunityLidershipAldeia(request):
	group = request.user.groups.all()[0].name
	municipality = Municipality.objects.all()
	userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
	if request.method == "POST":
		newid,_ = getnewid(CommunityLeadership)
		hashid = hash_md5(str(newid))
		form = CommunityLeadershipForm1(request.POST,user=userAddress)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.id = newid
			user = get_object_or_404(User,id=request.user.id)
			instance.user_created = user
			instance.hashed = hashid
			aldeia = form.cleaned_data['aldeia']
			instance.status = "Yes"
			municipality = get_object_or_404(Municipality,id=userAddress.employee.municipality.id)
			administrativepost = get_object_or_404(AdministrativePost,id=userAddress.employee.administrativepost.id)
			village = get_object_or_404(Village,id=userAddress.employee.village.id)
			instance.municipality = municipality
			instance.administrativepost = administrativepost
			instance.village = village
			instance.save()
			messages.success(request, f'Lideransa Aldeia Foun Adisiona ho Susesu.')
			return redirect('administration:communityLeadershipList')
	else:
		form = CommunityLeadershipForm1(user=userAddress)
	context = {
		"group":group,
		"title":"Adisiona Lideransa Komunitária",
		'commLeaderActive':"active",
		'page':"form",
		'municipality':municipality,
		'form':form,
	}
	return render(request, 'administration_layout/layout/communityLeadershipForm.html',context)

@login_required
@allowed_users(allowed_roles=['admin','xefe'])
def updateCommunityLidership(request,hashid):
	group = request.user.groups.all()[0].name
	communityLeadershipData = get_object_or_404(CommunityLeadership,hashed=hashid)
	userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
	if request.method == "POST":
		form = CommunityLeadershipUpdateForm(request.POST,instance=communityLeadershipData,user=userAddress,data=communityLeadershipData)
		if form.is_valid():
			form.save()
			messages.success(request, f'Dadus Lideransa Komunitária Altera ho Susesu.')
			return redirect('administration:communityLeadershipList')
	else:
		form = CommunityLeadershipUpdateForm(instance=communityLeadershipData,user=userAddress,data=communityLeadershipData)
	context = {
		"group":group,
		"title":"Altera Lideransa Komunitária",
		'commLeaderActive':"active",
		'page':"form",
		'form':form,
	}
	return render(request, 'administration_layout/layout/communityLeadershipForm.html',context)

@login_required
@allowed_users(allowed_roles=['admin','xefe'])
def terminateCommunityLeadership(request,hashid):
	leader = get_object_or_404(CommunityLeadership, hashed=hashid)
	leader.status = "No"
	leader.save()
	messages.success(request, f'Dadus Lideransa Komunitária Termina ho Susesu.')
	return redirect('administration:communityLeadershipList')

@login_required
def positionList(request):
	group = request.user.groups.all()[0].name
	if group == "admin":
		position = Position.objects.all().order_by('id')
	else:
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		position = Position.objects.all().order_by('id')
	context = {
		"group":group,
		"title":"Lista Kargu",
		'positionActive':"active",
		'page':"list",
		'positionList':position,
	}
	return render(request, 'administration_layout/layout/position.html',context)

@login_required
@allowed_users(allowed_roles=['admin'])
def addPosition(request):
	group = request.user.groups.all()[0].name
	if request.method == "POST":
		newid,_ = getnewid(Position)
		form = PositionForm(request.POST)
		if form.is_valid():
			instance=form.save(commit=False)
			instance.id=newid
			instance.save()
			messages.success(request, f'Kargu Foun Adisiona ho Susesu.')
			return redirect('administration:positionList')
	else:
		form = PositionForm()
	context = {
		"group":group,
		"title":"Adisiona Kargu",
		'positionActive':"active",
		'page':"add",
		'form':form,
	}
	return render(request, 'administration_layout/layout/position.html',context)

@login_required
@allowed_users(allowed_roles=['admin'])
def updatePosition(request,hashid):
	group = request.user.groups.all()[0].name
	position = get_object_or_404(Position,id=hashid)
	if request.method == "POST":
		form = PositionForm(request.POST,instance=position)
		if form.is_valid():
			form.save()
			messages.success(request, f'Kargu Altera ho Susesu.')
			return redirect('administration:positionList')
	else:
		form = PositionForm(instance=position)
	context = {
		"group":group,
		"title":"Altera Kargu",
		'positionActive':"active",
		'page':"update",
		'form':form,
	}
	return render(request, 'administration_layout/layout/position.html',context)

@login_required
@allowed_users(allowed_roles=['admin','xefe'])
def deleteCommunityLeadership(request,hashid):
	communityLeadershipData = get_object_or_404(CommunityLeadership,hashed=hashid)
	name = str(communityLeadershipData.position)+str(" ho naran ")+str(communityLeadershipData.population.name)
	communityLeadershipData.delete()
	messages.warning(request, f'Dados Lideransa Komunitária, {name} Hamoos ho Susesu.')
	return redirect('administration:communityLeadershipList')

@login_required
@allowed_users(allowed_roles=['admin'])
def deletePeriod(request,hashid):
	periodData = get_object_or_404(MandatePeriod,id=hashid)
	name = str(periodData.start)+str("-")+str(periodData.end)
	periodData.delete()
	messages.warning(request, f'Dadus Periodu {name} Hamoos ho Susesu.')
	return redirect('administration:periodList')
@login_required
@allowed_users(allowed_roles=['admin'])
def deletePosition(request,hashid):
	positionData = get_object_or_404(Position,id=hashid)
	name = str(positionData.name)
	positionData.delete()
	messages.warning(request, f'Dadus Kargu {name} Hamoos ho Susesu.')
	return redirect('administration:positionList')

@login_required
def viewCommunityLeadership(request,hashid):
	group = request.user.groups.all()[0].name
	communityLeadershipData = get_object_or_404(CommunityLeadership,hashed=hashid)
	context = {
		"group":group,
		"title":"Detallu Lideransa Komunitária",
		'commLeaderActive':"active",
		'page':"view",
		'communityLeadershipData':communityLeadershipData,
	}
	return render(request, 'administration_layout/layout/communityLeadershipForm.html',context)

@login_required
@allowed_users(allowed_roles=['admin','xefe'])
def changeCommunityLeadership(request,hashidPreviousLeader):
	group = request.user.groups.all()[0].name
	communityLeadershipToChange = get_object_or_404(CommunityLeadership,hashed=hashidPreviousLeader)
	village = communityLeadershipToChange.village
	municipalityid = get_object_or_404(Municipality,id=communityLeadershipToChange.municipality.id)
	administrativepostid = get_object_or_404(AdministrativePost,id=communityLeadershipToChange.administrativepost.id)
	villageid = get_object_or_404(Village,id=communityLeadershipToChange.village.id)
	if communityLeadershipToChange.position.name == "Xefe Aldeia":
		aldeia = communityLeadershipToChange.aldeia
		print("Tama")
	else:
		aldeia = ""
	if request.method == "POST":
		newid,_ = getnewid(CommunityLeadership)
		hashid = hash_md5(str(newid))
		form = ChangeCommunityLeadershipForm(request.POST,village=village)

		if form.is_valid():
			instance = form.save(commit=False)
			instance.id = newid
			instance.user_created = get_object_or_404(User,id=request.user.id)
			instance.hashed = hashid
			instance.position = communityLeadershipToChange.position
			instance.period = communityLeadershipToChange.period
			instance.status = "Yes"
			instance.municipality = municipalityid
			instance.administrativepost = administrativepostid
			instance.village = villageid
			instance.aldeia = aldeia
			instance.save()
			update = CommunityLeadership.objects.filter(hashed=hashidPreviousLeader).update(status="No",\
				endMandate=instance.startMandate)
			
			messages.success(request, f'Lideransa Komunitária Foun Adisiona ho Susesu.')
			return redirect('administration:communityLeadershipList')
	else:
		form = ChangeCommunityLeadershipForm(village=village)
	context = {
		"group":group,
		"title":"Adisiona Lideransa Komunitária",
		'commLeaderActive':"active",
		'communityLeadershipToChange':communityLeadershipToChange,
		'page':"form",
		'form':form,
	}
	return render(request, 'administration_layout/layout/communityLeadershipForm.html',context)
