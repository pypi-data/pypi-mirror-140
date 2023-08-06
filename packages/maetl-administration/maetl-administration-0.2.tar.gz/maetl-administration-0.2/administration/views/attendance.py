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
from main.decorators import *

# Create your views here.
@login_required
def decisionList(request):
	group = request.user.groups.all()[0].name
	if group == "admin":
		decisionList = Decision.objects.all().order_by('-id')
	else :
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		decisionList = Decision.objects.filter(village=userAddress.employee.village).order_by('-id')
	context = {
		"group":group,
		"title":"Lista Desizaun Enkontru",
		'attendanceActive':"active",
		'page':"decisionList",
		'decisionList':decisionList,
	}
	return render(request, 'administration_layout/layout/attendance.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def addAttendance(request, hashid):
	group = request.user.groups.all()[0].name
	decisionData = get_object_or_404(Decision,hashed=hashid)
	if request.method == "POST":
		newid = getjustnewid(Attendance)
		hashid = hash_md5(str(newid))
		form = AttendanceForm(request.POST)
		if form.is_valid():
			instance = form.save(commit=False)
			if instance.name == None:
				instance.name = request.POST.get("naranseluk")
			instance.id = newid
			instance.hashed = hashid
			instance.decision = decisionData
			year = get_object_or_404(Year,year=decisionData.year.year)
			instance.year = year
			user = get_object_or_404(User, id=request.user.id)
			instance.user_created = user
			userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
			instance.municipality = userAddress.employee.municipality
			instance.administrativepost = userAddress.employee.administrativepost
			instance.village = userAddress.employee.village
			instance.save()
			if 'save' in request.POST:
				messages.success(request, f'Lista Prezensa Adisiona ho Susesu.')
				return redirect('administration:decisionList')
			elif 'save_and_add_another' in request.POST:
				messages.success(request, f'Lista Prezensa Adisiona ho Susesu.')
				return redirect('administration:addAttendance',decisionData.hashed)
	else:
		form = AttendanceForm()
	context = {
		"group":group,
		"title":"Adisiona Lista Prezensa",
		'attendanceActive':"active",
		'page':"add",
		'form':form,
		'decisionData':decisionData,
	}
	return render(request, 'administration_layout/layout/attendanceForm.html',context)
	
@login_required
def viewAttendance(request,hashid):
	group = request.user.groups.all()[0].name
	decisionData = get_object_or_404(Decision,hashed=hashid)
	otherAttendance = Attendance.objects.filter(decision=decisionData).order_by('-id')
	villageAdviseAttendance = DecisionDetail.objects.filter(decision=decisionData,attendance="Yes")
	context = {
		"group":group,
		"title":f"Lista Prezensa, Data Enkontru : {decisionData.meeting_date.strftime('%d-%m-%Y')}",
		'attendanceActive':"active",
		'page':"viewMeetingAttendance",
		'decisionData':decisionData,
		'otherAttendance':otherAttendance,
		'villageAdviseAttendance':villageAdviseAttendance,
	}
	return render(request, 'administration_layout/layout/attendance.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def updateAttendance(request,hashidAttendance,hashidDecision):
	group = request.user.groups.all()[0].name
	attendanceData = get_object_or_404(Attendance,hashed=hashidAttendance)
	if request.method == "POST":
		form = AttendanceForm(request.POST,instance=attendanceData)
		if form.is_valid():
			instance = form.save(commit=False)
			if instance.name == None:
				instance.name = request.POST.get("naranseluk")
			instance.save()
			messages.success(request, f'Dadus Lista Prezensa Altera ho Susesu.')
			return redirect('administration:decisionList')
	else:
		form = AttendanceForm(instance=attendanceData)
	context = {
		"group":group,
		"title":f"Update Prezensa {attendanceData.name}",
		'attendanceActive':"active",
		'page':"update",
		'form':form,
		'attendanceData':attendanceData,
	}
	return render(request, 'administration_layout/layout/attendanceForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def deletePresence(request,hashidAttendance,hashidDecision):
	presenceData = get_object_or_404(Attendance,hashed=hashidAttendance)
	presenceData.delete()
	messages.error(request, f'Dadus Lista Prezensa {presenceData.name} Hamoos ho Susesu.')
	return redirect('administration:viewAttendance',hashidDecision)