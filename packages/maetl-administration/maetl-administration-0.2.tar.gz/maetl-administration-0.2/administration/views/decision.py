from django.shortcuts import render,redirect, get_object_or_404,HttpResponse
from django.contrib import messages
from ..forms import *
from ..models import *
from employee.models import *
from django.contrib.auth.models import User
from custom.utils import *
# pdf library
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.auth.decorators import login_required
from datetime import date
from main.decorators import *
# Create your views here.
@login_required
def villageAdviseDecisionList(request):
	group = request.user.groups.all()[0].name
	if group == "admin":
		decisionList = Decision.objects.filter(decision_type="Konsellu Suku").order_by('-id')
	else:
		userAddress = get_object_or_404(EmployeeUser, user__id=request.user.id)
		decisionList = Decision.objects.filter(decision_type="Konsellu Suku",village=userAddress.employee.village).order_by('-id')
	context = {
		"title":"Desizaun Konsellu Suku",
		'villageAdviseDecisionActive':"active",
		'decisionList':decisionList,
		'group':group,
	}
	return render(request, 'administration_layout/layout/decisionVillageAdvise.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def addDecisionVillageAdvise(request):
	group = request.user.groups.all()[0].name
	currentYear = date.today().year
	userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
	villageAdviseList = CommunityLeadership.objects.filter(status="Yes",village=userAddress.employee.village,position__name__in=("Xefe Suku","Xefe Aldeia","Delgadu","Delgada","Reprezentante Juventude Feto","Reprezentante Juventude Mane","Lia Nain"))
	yearList = Year.objects.all()
	if request.method == "POST":
		newid = getjustnewid(Decision)
		hashid = hash_md5(str(newid))
		decision_type = "Konsellu Suku"
		meeting_date = request.POST.get("meeting_date")
		decision_number = request.POST.get("decision_number")
		decision_on = request.POST.get("decision_on")
		observation = request.POST.get("observation")
		decision_on = decision_on.split(',')
		year = request.POST.get("year")
		year = get_object_or_404(Year,year=year)
		user_created = get_object_or_404(User,id=request.user.id)
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		villageAdviseData = request.POST.getlist('villageAdvise')
		# kondisaun bainhira konsellu suku la iha
		if villageAdviseData == []:
			messages.info(request, f'Dadus Konsellu Suku nebe partisipa iha enkontru seidauk hili. Favor Hili Konsellu Suku!')
			return redirect('administration:addDecisionVillageAdvise')
		decision = Decision.objects.create(id=newid,year=year,user_created=user_created,decision_type=decision_type,\
					meeting_date=meeting_date,decision_number=decision_number,observation=observation,hashed=hashid,\
					municipality=userAddress.employee.municipality,administrativepost=userAddress.employee.administrativepost,village=userAddress.employee.village)
		decision.save()
		for x in decision_on:
			newid = getjustnewid(VotingResult)
			hashid = hash_md5(str(newid))
			votingResult = VotingResult.objects.create(id=newid,hashed=hashid,decision=decision,decision_on=x,user_created=user_created,\
				vote_afavor=0,vote_kontra=0,vote_abstein=0,municipality=userAddress.employee.municipality,administrativepost=userAddress.employee.administrativepost,village=userAddress.employee.village)
			votingResult.save()
		villageAdviseOriginal = CommunityLeadership.objects.filter(status="Yes",village=userAddress.employee.village).iterator()
		for i in range(len(villageAdviseData)):
			villageAdviseIha = get_object_or_404(CommunityLeadership,hashed=villageAdviseData[i])
			decisionDetail = DecisionDetail.objects.create(decision=decision,villageAdvise=villageAdviseIha,attendance="Yes",\
				municipality=userAddress.employee.municipality,administrativepost=userAddress.employee.administrativepost,village=userAddress.employee.village)
			decisionDetail.save()
		for x in villageAdviseOriginal:
			if x.hashed not in villageAdviseData:
				villageAdviseLaiha = get_object_or_404(CommunityLeadership,hashed=x.hashed)
				decisionDetail = DecisionDetail.objects.create(decision=decision,villageAdvise=villageAdviseLaiha,attendance="No",\
					municipality=userAddress.employee.municipality,administrativepost=userAddress.employee.administrativepost,village=userAddress.employee.village)
		messages.success(request, f'Desizaun Konsellu Suku Adisiona ho Susesu.')
		return redirect('administration:villageAdviseDecisionList')
	context = {
		"group":group,
		"title":"Adisiona Desizaun Konsellu Suku",
		'villageAdviseDecisionActive':"active",
		'page':"add",
		"yearList":yearList,
		"villageAdviseList":villageAdviseList,
		"currentYear":currentYear,
	}
	return render(request, 'administration_layout/layout/decisionVillageAdviseForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def addDecisionResult(request,decisionHashid):
	group = request.user.groups.all()[0].name
	decisionData = get_object_or_404(Decision, hashed=decisionHashid)
	if request.method == "POST":
		newid = getjustnewid(VotingResult)
		hashid = hash_md5(str(newid))
		form = DecisionResultForm(request.POST)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.id = newid
			instance.hashed = hashid
			instance.decision = decisionData
			user = get_object_or_404(User, id=request.user.id)
			userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
			instance.user_created = user
			instance.municipality=userAddress.employee.municipality
			instance.administrativepost=userAddress.employee.administrativepost
			instance.village=userAddress.employee.village
			instance.save()
			messages.success(request, f'Rezultadu Desizaun kona-ba {instance.decision_on} Adisiona ho Susesu.')
			return redirect('administration:villageAdviseDecisionList')
	else :
		form = DecisionResultForm()
	context = {
		"group":group,
		"title":f"Adisiona Rezultadu Desizaun",
		'villageAdviseDecisionActive':"active",
		'cardTitle':str(" : ") +str(decisionData.meeting_date)+str(" / ") +str(decisionData.decision_number),
		'page':"addDecisionResult",
		'form':form,
	}
	return render(request, 'administration_layout/layout/decisionVillageAdviseForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def addDecisionResult1(request,decisionHashid):
	group = request.user.groups.all()[0].name
	decisionData = get_object_or_404(Decision, hashed=decisionHashid)
	if request.method == "POST":
		newid = getjustnewid(VotingResult)
		hashid = hash_md5(str(newid))
		form = DecisionResultForm(request.POST)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.id = newid
			instance.hashed = hashid
			instance.decision = decisionData
			user = get_object_or_404(User, id=request.user.id)
			instance.user_created = user
			userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
			instance.municipality=userAddress.employee.municipality
			instance.administrativepost=userAddress.employee.administrativepost
			instance.village=userAddress.employee.village
			instance.save()
			messages.success(request, f'Rezultadu Desizaun kona-ba {instance.decision_on} Adisiona ho Susesu.')
			return redirect('administration:villageChiefDecisionList')
	else :
		form = DecisionResultForm()
	context = {
		"group":group,
		"title":f"Adisiona Rezultadu Desizaun",
		'villageChiefDecisionActive':"active",
		'cardTitle':str(" : ") +str(decisionData.meeting_date)+str(" / ") +str(decisionData.decision_number),
		'page':"addDecisionResult",
		'form':form,
	}
	return render(request, 'administration_layout/layout/decisionVillageChiefForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def updateVotingResult(request,hashid,decision):
	group = request.user.groups.all()[0].name
	decisionData = get_object_or_404(Decision, hashed=decision)
	votingResult = get_object_or_404(VotingResult, hashed=hashid)
	if request.method == "POST":
		form = DecisionResultForm(request.POST,instance=votingResult)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.save()
			messages.success(request, f'Rezultadu Desizaun kona-ba {instance.decision_on} Altera ho Susesu.')
			return redirect('administration:viewDecisionVillageAdvise',decision)
	else :
		form = DecisionResultForm(instance=votingResult)
	context = {
		"group":group,
		"title":f"Adisiona Rezultadu Desizaun",
		'villageAdviseDecisionActive':"active",
		'cardTitle':str(" : ") +str(decisionData.meeting_date)+str(" / ") +str(decisionData.decision_number),
		'page':"addDecisionResult",
		'form':form,
	}
	return render(request, 'administration_layout/layout/decisionVillageAdviseForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def updateVotingResult1(request,hashid,decision):
	group = request.user.groups.all()[0].name
	decisionData = get_object_or_404(Decision, hashed=decision)
	votingResult = get_object_or_404(VotingResult, hashed=hashid)
	if request.method == "POST":
		form = DecisionResultForm(request.POST,instance=votingResult)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.save()
			messages.success(request, f'Rezultadu Desizaun kona-ba {instance.decision_on} Altera ho Susesu.')
			return redirect('administration:viewDecisionVillageChief',decision)
	else :
		form = DecisionResultForm(instance=votingResult)
	context = {
		"group":group,
		"title":f"Adisiona Rezultadu Desizaun",
		'villageChiefDecisionActive':"active",
		'cardTitle':str(" : ") +str(decisionData.meeting_date)+str(" / ") +str(decisionData.decision_number),
		'page':"addDecisionResult",
		'form':form,
	}
	return render(request, 'administration_layout/layout/decisionVillageChiefForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def deleteDecisionVillageAdvise(request,hashid):
	decisionData = get_object_or_404(Decision,hashed=hashid)
	name = decisionData
	decisionData.delete()
	messages.error(request, f'Dadus Konsellu Suku {name} Hamoos ho Susesu.')
	return redirect('administration:villageAdviseDecisionList')

@login_required
def villageChiefDecisionList(request):
	group = request.user.groups.all()[0].name
	if group == "admin":
		decisionList = Decision.objects.filter(decision_type="Xefe Suku").order_by('-id')
	else:
		userAddress = get_object_or_404(EmployeeUser, user__id=request.user.id)
		decisionList = Decision.objects.filter(decision_type="Xefe Suku",village=userAddress.employee.village).order_by('-id')
	context = {
		"group":group,
		"title":"Desizaun Xefe Suku",
		'villageChiefDecisionActive':"active",
		'decisionList':decisionList,
		'group':group,
	}
	return render(request, 'administration_layout/layout/decisionVillageChief.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def addDecisionVillageChief(request):
	group = request.user.groups.all()[0].name
	userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
	villageAdviseList = CommunityLeadership.objects.filter(status="Yes",village=userAddress.employee.village,position__name__in=("Xefe Suku","Xefe Aldeia","Delgadu","Delgada","Reprezentante Juventude Feto","Reprezentante Juventude Mane","Lia Nain"))
	yearList = Year.objects.all()
	if request.method == "POST":
		newid = getjustnewid(Decision)
		hashid = hash_md5(str(newid))
		decision_type = "Xefe Suku"
		meeting_date = request.POST.get("meeting_date")
		decision_number = request.POST.get("decision_number")
		decision_on = request.POST.get("decision_on")
		observation = request.POST.get("observation")
		decision_on = decision_on.split(',')
		year = request.POST.get("year")
		year = get_object_or_404(Year,year=year)
		user_created = get_object_or_404(User,id=request.user.id)
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		villageAdviseData = request.POST.getlist('villageAdvise')
		# kondisaun bainhira konsellu suku la iha
		if villageAdviseData == []:
			messages.info(request, f'Dadus Konsellu Suku nebe partisipa iha enkontru seidauk hili. Favor Hili Konsellu Suku!')
			return redirect('administration:addDecisionVillageChief')
		decision = Decision.objects.create(id=newid,year=year,user_created=user_created,decision_type=decision_type,\
					meeting_date=meeting_date,decision_number=decision_number,observation=observation,hashed=hashid,\
					municipality=userAddress.employee.municipality,administrativepost=userAddress.employee.administrativepost,village=userAddress.employee.village)
		decision.save()
		for x in decision_on:
			newid = getjustnewid(VotingResult)
			hashid = hash_md5(str(newid))
			votingResult = VotingResult.objects.create(id=newid,hashed=hashid,decision=decision,decision_on=x,user_created=user_created,\
				vote_afavor=0,vote_kontra=0,vote_abstein=0,municipality=userAddress.employee.municipality,administrativepost=userAddress.employee.administrativepost,village=userAddress.employee.village)
			votingResult.save()
		villageAdviseOriginal = CommunityLeadership.objects.filter(status="Yes",village=userAddress.employee.village).iterator()
		for i in range(len(villageAdviseData)):
			villageAdviseIha = get_object_or_404(CommunityLeadership,hashed=villageAdviseData[i])
			decisionDetail = DecisionDetail.objects.create(decision=decision,villageAdvise=villageAdviseIha,attendance="Yes",\
				municipality=userAddress.employee.municipality,administrativepost=userAddress.employee.administrativepost,village=userAddress.employee.village)
			decisionDetail.save()
		for x in villageAdviseOriginal:
			if x.hashed not in villageAdviseData:
				villageAdviseLaiha = get_object_or_404(CommunityLeadership,hashed=x.hashed)
				decisionDetail = DecisionDetail.objects.create(decision=decision,villageAdvise=villageAdviseLaiha,attendance="No",\
					municipality=userAddress.employee.municipality,administrativepost=userAddress.employee.administrativepost,village=userAddress.employee.village)
		messages.success(request, f'Desizaun Xefe Suku Adisiona ho Susesu.')
		return redirect('administration:villageChiefDecisionList')
	context = {
		"group":group,
		"title":"Adisiona Desizaun Xefe Suku",
		'villageChiefDecisionActive':"active",
		'page':"add",
		"yearList":yearList,
		"villageAdviseList":villageAdviseList,
	}
	return render(request, 'administration_layout/layout/decisionVillageChiefForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def updateDecisionVillageChief(request, hashid):
	group = request.user.groups.all()[0].name
	decisionData = get_object_or_404(Decision,hashed=hashid)
	villageAdviseList = DecisionDetail.objects.filter(decision=decisionData)
	yearList = Year.objects.all()
	if request.method == "POST":
		meeting_date = request.POST.get("meeting_date")
		decision_number = request.POST.get("decision_number")
		year = request.POST.get("year")
		year = get_object_or_404(Year,year=year)
		decision = Decision.objects.filter(hashed=hashid).update(meeting_date=meeting_date,decision_number=decision_number,\
					year=year)
		villageAdviseOriginal = CommunityLeadership.objects.filter(status="Yes").iterator()
		villageAdviseData = request.POST.getlist('villageAdvise')
		for i in range(len(villageAdviseData)):
			villageAdviseIha = get_object_or_404(CommunityLeadership,hashed=villageAdviseData[i])
			decisionDetail = DecisionDetail.objects.filter(decision__hashed=hashid,villageAdvise=villageAdviseIha).update(attendance="Yes")
		for x in villageAdviseOriginal:
			if x.hashed not in villageAdviseData:
				villageAdviseLaiha = get_object_or_404(CommunityLeadership,hashed=x.hashed)
				decisionDetail = DecisionDetail.objects.filter(decision__hashed=hashid,villageAdvise=villageAdviseLaiha).update(attendance="No")
		messages.success(request, f'Dadus Desizaun Xefe Suku Altera ho Susesu.')
		return redirect('administration:villageChiefDecisionList')
	context = {
		"group":group,
		"title":"Update Desizaun Xefe Suku",
		'villageChiefDecisionActive':"active",
		'page':"update",
		"yearList":yearList,
		"decisionData":decisionData,
		"villageAdviseList":villageAdviseList,
	}
	return render(request, 'administration_layout/layout/decisionVillageChiefForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def updateDecisionVillageAdvise(request, hashid):
	group = request.user.groups.all()[0].name
	decisionData = get_object_or_404(Decision,hashed=hashid)
	villageAdviseList = DecisionDetail.objects.filter(decision=decisionData)
	yearList = Year.objects.all()
	if request.method == "POST":
		meeting_date = request.POST.get("meeting_date")
		decision_number = request.POST.get("decision_number")
		year = request.POST.get("year")
		year = get_object_or_404(Year,year=year)
		decision = Decision.objects.filter(hashed=hashid).update(meeting_date=meeting_date,decision_number=decision_number,\
					year=year)
		villageAdviseOriginal = CommunityLeadership.objects.filter(status="Yes").iterator()
		villageAdviseData = request.POST.getlist('villageAdvise')
		for i in range(len(villageAdviseData)):
			villageAdviseIha = get_object_or_404(CommunityLeadership,hashed=villageAdviseData[i])
			decisionDetail = DecisionDetail.objects.filter(decision__hashed=hashid,villageAdvise=villageAdviseIha).update(attendance="Yes")
		for x in villageAdviseOriginal:
			if x.hashed not in villageAdviseData:
				villageAdviseLaiha = get_object_or_404(CommunityLeadership,hashed=x.hashed)
				decisionDetail = DecisionDetail.objects.filter(decision__hashed=hashid,villageAdvise=villageAdviseLaiha).update(attendance="No")
		messages.success(request, f'Dadus Desizaun Konsellu Suku Altera ho Susesu.')
		return redirect('administration:villageAdviseDecisionList')
	context = {
		"group":group,
		"title":"Update Desizaun Konsellu Suku",
		'villageAdviseDecisionActive':"active",
		'page':"update",
		"yearList":yearList,
		"decisionData":decisionData,
		"villageAdviseList":villageAdviseList,
	}
	return render(request, 'administration_layout/layout/decisionVillageAdviseForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def deleteDecisionVillageChief(request, hashid):
	decisionData = get_object_or_404(Decision,hashed=hashid)
	name = decisionData
	decisionData.delete()
	messages.warning(request, f'Dadus Desizaun Xefe Suku {name} Hamoos ho Susesu')
	return redirect('administration:villageChiefDecisionList')

@login_required
def viewDecisionVillageAdvise(request,hashid):
	group = request.user.groups.all()[0].name
	decisionData = get_object_or_404(Decision,decision_type="Konsellu Suku",hashed=hashid)
	context = {
		"group":group,
		"title":"Detallu Desizaun Konsellu Suku",
		'villageAdviseDecisionActive':"active",
		'page':"view",
		"decisionData":decisionData,
	}
	return render(request, 'administration_layout/layout/decisionVillageAdviseForm.html',context)

@login_required
def viewDecisionVillageChief(request,hashid):
	group = request.user.groups.all()[0].name
	decisionData = get_object_or_404(Decision,decision_type="Xefe Suku",hashed=hashid)
	context = {
		"group":group,
		"title":"Detallu Desizaun Xefe Suku",
		'villageChiefDecisionActive':"active",
		'page':"view",
		"decisionData":decisionData,
	}
	return render(request, 'administration_layout/layout/decisionVillageChiefForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def deleteVotingResult(request,hashid,decision):
	votingResult = get_object_or_404(VotingResult,hashed=hashid)
	name = votingResult.decision_on
	votingResult.delete()
	messages.warning(request, f'Dadus Desizaun kona-ba {name} Hamoos ho Susesu')
	return redirect('administration:viewDecisionVillageAdvise',decision)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def deleteVotingResult1(request,hashid,decision):
	name = votingResult.decision_on
	votingResult.delete()
	messages.warning(request, f'Dadus Desizaun kona-ba {name} Hamoos ho Susesu')
	return redirect('administration:viewDecisionVillageChief',decision)
