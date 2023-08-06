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
def visitorList(request):
	group = request.user.groups.all()[0].name
	if group == "admin":
		visitorList = Visitor.objects.all().order_by('-id')
	else:
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		visitorList = Visitor.objects.filter(village=userAddress.employee.village).order_by('-id')
	context = {
		"group":group,
		"title":"Bainaka Suku",
		'visitorActive':"active",
		'visitorList':visitorList,
	}
	return render(request, 'administration_layout/layout/visitor.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def addVisitor(request):
	group = request.user.groups.all()[0].name
	if request.method == "POST":
		newid,_ = getnewid(Visitor)
		hashid = hash_md5(str(newid))

		form = VisitorForm(request.POST)
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
			messages.success(request, f'Dadus Bainaka Suku Adisiona ho Susesu.')
			return redirect('administration:visitorList')
	else :
		form = VisitorForm()
	context = {
		"group":group,
		"title":"Adisiona Dadus Bainaka",
		"form":form,
		"page":"add",
		"visitorActive":"active",
	}
	return render(request, 'administration_layout/layout/visitorForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def updateVisitor(request,hashid):
	group = request.user.groups.all()[0].name
	visitorData = get_object_or_404(Visitor,hashed=hashid)
	if request.method == "POST":
		form = VisitorForm(request.POST,instance=visitorData)
		if form.is_valid():
			form.save()
			messages.success(request, f'Dadus Bainaka Suku Altera ho Susesu.')
			return redirect('administration:visitorList')
	else :
		form = VisitorForm(instance=visitorData)
	context = {
		"group":group,
		"title":"Update Dadus Bainaka",
		"form":form,
		"page":"update",
		"visitorActive":"active",
	}
	return render(request, 'administration_layout/layout/visitorForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def deleteVisitor(request,hashid):
	visitorData = get_object_or_404(Visitor,hashed=hashid)
	visitorName = visitorData.name
	visitorData.delete()
	messages.error(request, f'Dadus Bainaka {visitorName} Hamoos ho Susesu.')
	return redirect('administration:visitorList')

	

