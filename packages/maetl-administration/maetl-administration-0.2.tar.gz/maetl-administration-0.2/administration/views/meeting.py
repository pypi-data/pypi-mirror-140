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
def meetingList(request):
	group = request.user.groups.all()[0].name
	if group == "admin":
		meetingList = MeetingTime.objects.all().order_by('-id')
		inner_qs = MeetingTime.objects.values_list('decision__id',flat=True)
		decisionList = Decision.objects.exclude(id__in=inner_qs)
	else:
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		meetingList = MeetingTime.objects.filter(village=userAddress.employee.village).order_by('-id')
		inner_qs = MeetingTime.objects.values_list('decision__id',flat=True)
		decisionList = Decision.objects.exclude(id__in=inner_qs).filter(village=userAddress.employee.village)
	context = {
		"group":group,
		"title":"Lista Minutas Enkontru Suku",
		'meetingActive':"active",
		'decisionList':decisionList,
		'meetingList':meetingList,
	}
	return render(request, 'administration_layout/layout/meeting.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def addMeeting(request,decisionId):
	group = request.user.groups.all()[0].name
	currentYear = date.today().year
	userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
	villageAdviseAbsentInDecision = DecisionDetail.objects.filter(decision__hashed=decisionId,attendance="No")
	xefe_suku = get_object_or_404(CommunityLeadership,village=userAddress.employee.village,status="Yes",position__name="Xefe Suku")
	decision = get_object_or_404(Decision,hashed=decisionId)
	getVotingResult = VotingResult.objects.filter(decision=decision)
	agenda = ""
	for x in getVotingResult:
		agenda += x.decision_on+","
	agenda = list(agenda)[:-1]
	last_agenda = ""
	for i in agenda:
		last_agenda += i

	year = Year.objects.all()
	if request.method == "POST":
		form = MeetingForm(request.POST)
		newid = getjustnewid(MeetingTime)
		hashid = hash_md5(str(newid))
		if form.is_valid():
			instance = form.save(commit=False)
			instance.id = newid
			instance.hashed = hashid
			user = get_object_or_404(User, id=request.user.id)
			instance.user_created = user
			userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
			instance.municipality = userAddress.employee.municipality
			instance.administrativepost = userAddress.employee.administrativepost
			instance.village = userAddress.employee.village
			year = request.POST.get('year')
			year = get_object_or_404(Year,year=year)
			instance.year = year
			instance.lideransa_komunitaria = xefe_suku
			instance.decision = decision
			instance.meeting_agenda = last_agenda
			instance.save()
			messages.success(request, f'Dadus Minutas Enkontru Adisiona ho Susesu.')
			return redirect('administration:meetingList')
	else :
		form = MeetingForm()
	context = {
		"form":form,
		"group":group,
		"title":"Adisiona Minutas Enkontru Suku",
		'meetingActive':"active",
		'page':"add",
		'villageAdviseAbsentInDecision':villageAdviseAbsentInDecision,
		'currentYear':currentYear,
		'year':year,
		'decision':decision,
		'getVotingResult':getVotingResult,
		'xefe_suku':xefe_suku,
	}
	return render(request, 'administration_layout/layout/meetingForm.html',context)

@login_required
def viewMeetingMinutes(request, hashid):
	group = request.user.groups.all()[0].name
	meetingMinutes = get_object_or_404(MeetingTime,hashed=hashid)
	meetingDecision = get_object_or_404(Decision,hashed=meetingMinutes.decision.hashed)
	villageAdviseAbsentInDecision = DecisionDetail.objects.filter(decision__hashed=meetingDecision.hashed,attendance="No")
	context = {
		"group":group,
		"title":"Detallu Minutas Enkontru Suku",
		'meetingActive':"active",
		'page':"view",
		'meetingMinutes':meetingMinutes,
		'villageAdviseAbsentInDecision':villageAdviseAbsentInDecision,
	}
	return render(request, 'administration_layout/layout/meetingForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def updateMeetingMinutes(request, hashid):
	group = request.user.groups.all()[0].name
	meetingMinutes = get_object_or_404(MeetingTime,hashed=hashid)
	decision = get_object_or_404(Decision,hashed=meetingMinutes.decision.hashed)
	villageAdviseAbsentInDecision = DecisionDetail.objects.filter(decision__hashed=decision.hashed,attendance="No")
	getVotingResult = VotingResult.objects.filter(decision=decision)
	year = Year.objects.all()
	if request.method == "POST":
		form = MeetingForm(request.POST,instance=meetingMinutes)
		if form.is_valid():
			instance = form.save(commit=False)
			year = request.POST.get('year')
			year = get_object_or_404(Year,year=year)
			instance.year = year
			instance.save()
		messages.success(request, f'Dadus Minutas Enkontru Altera ho Susesu.')
		return redirect('administration:viewMeetingMinutes',hashid)
	else :
		form = MeetingForm(instance=meetingMinutes)
	context = {
		"form":form,
		"group":group,
		"title":"Update Minutas Enkontru Suku",
		'meetingActive':"active",
		'page':"update",
		'currentYear':meetingMinutes.year,
		'xefe_suku':meetingMinutes.lideransa_komunitaria,
		'year':year,
		'decision':decision,
		'meetingMinutes':meetingMinutes,
		'getVotingResult':getVotingResult,
		'villageAdviseAbsentInDecision':villageAdviseAbsentInDecision,
	}
	return render(request, 'administration_layout/layout/meetingForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def deleteMeetingMinutes(request, hashid):
	meetingMinutesData = get_object_or_404(MeetingTime,hashed=hashid)
	meetingMinutesData.delete()
	messages.error(request, f'Dadus Minutas Enkontru Hamoos ho Susesu.')
	return redirect('administration:meetingList')
