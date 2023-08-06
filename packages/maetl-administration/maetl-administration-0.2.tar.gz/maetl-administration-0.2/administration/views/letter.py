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
from custom.models import *
from datetime import date
from main.decorators import *
# Create your views here.
@login_required
def letterInList(request):
	group = request.user.groups.all()[0].name
	if group == "admin":
		letterIn = LetterIn.objects.all().order_by('-id')
	else:
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		letterIn = LetterIn.objects.filter(village=userAddress.employee.village).order_by('-id')
	context = {
		"group":group,
		"title":"Karta Tama",
		"letterInActive":"active",
		"letterInList":letterIn,
	}
	return render(request, 'administration_layout/layout/letterIn.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def addLetterIn(request):
	group = request.user.groups.all()[0].name
	if request.method == "POST":
		newid,_ = getnewid(LetterIn)
		hashid = hash_md5(str(newid))

		form = LetterInForm(request.POST,request.FILES)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.id = newid
			instance.user_created = request.user
			instance.hashed = hashid
			userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
			instance.municipality = userAddress.employee.municipality
			instance.administrativepost = userAddress.employee.administrativepost
			instance.village = userAddress.employee.village
			instance.save()
			messages.success(request, f'Karta Tama Foun Adisiona ho Susesu.')
			return redirect('administration:letterInList')
	else :
		form = LetterInForm()
	context = {
		"group":group,
		"title":"Adisiona Karta Tama",
		"form":form,
		"letterInActive":"active",
	}
	return render(request, 'administration_layout/layout/letterInForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def updateLetterIn(request,hashid):
	group = request.user.groups.all()[0].name
	letterInData = get_object_or_404(LetterIn,hashed=hashid)
	if request.method == "POST":
		form = LetterInForm(request.POST,request.FILES,instance=letterInData)
		if form.is_valid():
			form.save()
			messages.success(request, f'Dadus Karta Tama Altera ho Susesu.')
			return redirect('administration:letterInList')
	else :
		form = LetterInForm(instance=letterInData)
	context = {
		"group":group,
		"title":"Update Karta Tama",
		"form":form,
		"letterInActive":"active",
	}
	return render(request, 'administration_layout/layout/letterInForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def deleteLetterIn(request, hashid):
	group = request.user.groups.all()[0].name
	letterInData = get_object_or_404(LetterIn,hashed=hashid)
	name=letterInData.subject
	letterInData.delete()
	messages.error(request, f'Dadus Karta Tama {name} Hamoos ho Susesu.')
	return redirect('administration:letterInList')

@login_required
def letterOutList(request):
	group = request.user.groups.all()[0].name
	if group == "admin":
		letterOutList = LetterOut.objects.all().order_by('-id')
	else:
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		letterOutList = LetterOut.objects.filter(village=userAddress.employee.village).order_by('-id')
	context = {
		"group":group,
		"title":"Karta Sai",
		"letterOutActive":"active",
		"letterOutList":letterOutList,
	}
	return render(request, 'administration_layout/layout/letterOut.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def addLetterOut(request):
	group = request.user.groups.all()[0].name
	if request.method == "POST":
		newid,_ = getnewid(LetterOut)
		hashid = hash_md5(str(newid))
		form = LetterOutForm(request.POST,request.FILES)
		if form.is_valid():
			print("tama")
			instance = form.save(commit=False)
			instance.id = newid
			instance.user_created = request.user
			instance.hashed = hashid
			userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
			instance.municipality = userAddress.employee.municipality
			instance.administrativepost = userAddress.employee.administrativepost
			instance.village = userAddress.employee.village
			instance.save()
			messages.success(request, f'Dadus Karta Sai Adisiona ho Susesu.')
			return redirect('administration:letterOutList')
	else:
		form = LetterOutForm()
	context = {
		"group":group,
		"title":"Adisiona Karta Sai",
		"letterOutActive":"active",
		"form":form,
	}
	return render(request, 'administration_layout/layout/letterOutForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def updateLetterOut(request,hashid):
	group = request.user.groups.all()[0].name
	letterOutData = get_object_or_404(LetterOut,hashed=hashid)
	if request.method == "POST":
		form = LetterOutForm(request.POST,request.FILES,instance=letterOutData)
		if form.is_valid():
			form.save()
			messages.success(request, f'Dadus Karta Sai Altera ho Susesu.')
			return redirect('administration:letterOutList')
	else:
		form = LetterOutForm(instance=letterOutData)
	context = {
		"group":group,
		"title":"Adisiona Karta Sai",
		"letterOutActive":"active",
		"form":form,
	}
	return render(request, 'administration_layout/layout/letterOutForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def deleteLetterOut(request, hashid):
	letterOutData = get_object_or_404(LetterOut,hashed=hashid)
	name=letterOutData.subject
	letterOutData.delete()
	messages.error(request, f'Dadus Karta Sai {name} Hamoos ho Susesu.')
	return redirect('administration:letterOutList')

@login_required
def expeditionList(request):
	group = request.user.groups.all()[0].name
	if group == "admin":
		expeditionList = LetterOut.objects.all().order_by('-id')
	else:
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		expeditionList = LetterOut.objects.filter(village=userAddress.employee.village).order_by('-id')
	context = {
		"group":group,
		"title":"Lista Espedisaun",
		"expeditionActive":"active",
		"expeditionList":expeditionList,
	}
	return render(request, 'administration_layout/layout/expedition.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def addExpedition(request,hashid):
	group = request.user.groups.all()[0].name
	letterOut = get_object_or_404(LetterOut,hashed=hashid)
	if request.method == "POST":
		newid = getjustnewid(LetterOutExpedition)
		hashid = hash_md5(str(newid))
		form = ExpeditionForm(request.POST)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.id = newid
			instance.user_created = request.user
			instance.hashed = hashid
			instance.letter_out = letterOut
			userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
			instance.municipality = userAddress.employee.municipality
			instance.administrativepost = userAddress.employee.administrativepost
			instance.village = userAddress.employee.village
			instance.save()
			messages.success(request, f'Dadus Espedisaun Adisiona ho Susesu.')
			return redirect('administration:viewExpeditionDetail',letterOut.hashed)
	else:
		form = ExpeditionForm()
	context = {
		"group":group,
		"title":f"Adisiona Dadus Espedisaun",
		"expeditionActive":"active",
		"page":"add",
		"letterOut":letterOut,
		"form":form,
	}
	return render(request, 'administration_layout/layout/expeditionForm.html',context)

@login_required
def viewExpeditionDetail(request,hashid):
	group = request.user.groups.all()[0].name
	letterOut = get_object_or_404(LetterOut,hashed=hashid)
	expeditionData = LetterOutExpedition.objects.filter(letter_out=letterOut).order_by('-id')
	context = {
		"group":group,
		"title":f"Detallu Dadus Espedisaun",
		"expeditionActive":"active",
		"page":"viewDetail",
		"letterOut":letterOut,
		"expeditionData":expeditionData,
	}
	return render(request, 'administration_layout/layout/expeditionForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def uploadExpeditionFile(request,hashid):
	group = request.user.groups.all()[0].name
	letterOutData = get_object_or_404(LetterOut,hashed=hashid)
	if request.method == "POST":
		newid = getjustnewid(AttachedExpedition)
		hashid = hash_md5(str(newid))
		form = AttachedExpeditionForm(request.POST,request.FILES)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.letter_out = letterOutData
			instance.id = newid
			instance.hashed = hashid
			instance.user_created = request.user
			userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
			instance.municipality = userAddress.employee.municipality
			instance.administrativepost = userAddress.employee.administrativepost
			instance.village = userAddress.employee.village
			instance.save()
			messages.success(request, f'File Aneksu Espedisaun Adisiona ho Susesu.')
			return redirect('administration:viewExpeditionDetail',letterOutData.hashed)
	else:
		form = AttachedExpeditionForm()
	context = {
		"group":group,
		"title":f"Upload File Aneksu Espedisaun",
		"expeditionActive":"active",
		"page":"uploadFile",
		"letterOutData":letterOutData,
		"form":form,
	}
	return render(request, 'administration_layout/layout/expeditionForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def updateFileExpedition(request,hashid):
	group = request.user.groups.all()[0].name
	previousFile = get_object_or_404(AttachedExpedition,hashed=hashid)
	if request.method == "POST":
		form = AttachedExpeditionForm(request.POST,request.FILES,instance=previousFile)
		if form.is_valid():
			form.save()
			messages.success(request, f'File Aneksu Espedisaun Altera ho Susesu.')
			return redirect('administration:viewExpeditionDetail',previousFile.letter_out.hashed)
	else:
		form = AttachedExpeditionForm(instance=previousFile)
	context = {
		"group":group,
		"title":f"Update File Aneksu Espedisaun",
		"expeditionActive":"active",
		"page":"uploadFile",
		"form":form,
	}
	return render(request, 'administration_layout/layout/expeditionForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def updateExpedition(request,hashid):
	group = request.user.groups.all()[0].name
	expeditionData = get_object_or_404(LetterOutExpedition,hashed=hashid)
	if request.method == "POST":
		form = ExpeditionForm(request.POST,request.FILES,instance=expeditionData)
		if form.is_valid():
			form.save()
			messages.success(request, f'Dadus Espedisaun Altera ho Susesu.')
			return redirect('administration:expeditionList')
	else:
		form = ExpeditionForm(instance=expeditionData)
	context = {
		"group":group,
		"title":f"Update Dadus Espedisaun",
		"expeditionActive":"active",
		"page":"update",
		"form":form,
	}
	return render(request, 'administration_layout/layout/expeditionForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def deleteExpedition(request,hashid):
	expeditionData = get_object_or_404(LetterOutExpedition,hashed=hashid)
	name=expeditionData.sent_to
	expeditionData.delete()
	messages.error(request, f'Dadus Espedisaun Haruka ba {name} Hamoos ho Susesu.')
	return redirect('administration:expeditionList')

@login_required
def complaintList(request):
	group = request.user.groups.all()[0].name
	if group == "admin":
		complaintList = Complaint.objects.all()
	else:
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		complaintList = Complaint.objects.filter(village=userAddress.employee.village)
	context = {
		"group":group,
		"title":"Rejistu Keixa Suku",
		"complaintActive":"active",
		"complaintList":complaintList,
	}
	return render(request, 'administration_layout/layout/complaint.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def addComplaint(request):
	group = request.user.groups.all()[0].name
	if request.method == "POST":
		newid = getjustnewid(Complaint)
		hashid = hash_md5(str(newid))
		form = ComplaintForm(request.POST)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.id = newid
			instance.user_created = request.user
			instance.hashed = hashid
			userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
			instance.municipality = userAddress.employee.municipality
			instance.administrativepost = userAddress.employee.administrativepost
			instance.village = userAddress.employee.village
			instance.save()
			messages.success(request, f'Dadus Keixa Suku Adisiona ho Susesu.')
			return redirect('administration:complaintList')
	else:
		form = ComplaintForm()
	context = {
		"group":group,
		"title":"Adisiona Keixa Suku",
		"complaintActive":"active",
		"form":form,
		"page":"add",
	}
	return render(request, 'administration_layout/layout/complaintForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def updateComplaint(request,hashid):
	group = request.user.groups.all()[0].name
	complaintData = get_object_or_404(Complaint,hashed=hashid)
	if request.method == "POST":
		form = ComplaintForm(request.POST,instance=complaintData)
		if form.is_valid():
			form.save()
			messages.success(request, f'Dadus Keixa Suku Altera ho Susesu.')
			return redirect('administration:complaintList')
	else:
		form = ComplaintForm(instance=complaintData)
	context = {
		"group":group,
		"title":"Update Keixa Suku",
		"complaintActive":"active",
		"form":form,
		"page":"update",
	}
	return render(request, 'administration_layout/layout/complaintForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def deleteComplaint(request,hashid):
	complaintData = get_object_or_404(Complaint,hashed=hashid)
	name=complaintData.subject
	complaintData.delete()
	messages.error(request, f'Dadus Keixa Suku {name} Hamoos ho Susesu.')
	return redirect('administration:complaintList')
	
