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
from employee.models import *
import xlwt
# Create your views here.
@login_required
def inventoryList(request):
	group = request.user.groups.all()[0].name
	if group == "admin":
		inventoryList = Inventory.objects.all().order_by('-id')
	else:
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		inventoryList = Inventory.objects.filter(village=userAddress.employee.village).order_by('-id')
	context = {
		"group":group,
		"title":"Lista Inventária",
		'inventoryActive':"active",
		'inventoryList':inventoryList,
	}
	return render(request, 'administration_layout/layout/inventory.html',context)

@login_required
def usedInventoryList(request):
	group = request.user.groups.all()[0].name
	if group == "admin":
		usedInventoryDetail = UsedInventoryDetail.objects.all().order_by('-id')
	else:
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		usedInventoryDetail = UsedInventoryDetail.objects.filter(village=userAddress.employee.village).order_by('-id')
	context = {
		"group":group,
		"title":"Lista Inventária Uzadu",
		'usedInventoryActive':"active",
		'usedInventoryDetail':usedInventoryDetail,
	}
	return render(request, 'administration_layout/layout/usedInventory.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def addInventory(request):
	group = request.user.groups.all()[0].name
	if request.method == "POST":
		newid = getjustnewid(Inventory)
		hashid = hash_md5(str(newid))
		form = InventoryForm(request.POST)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.id = newid
			instance.hashed = hashid
			user = User.objects.get(id=request.user.id)
			instance.user_created = user
			userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
			instance.municipality = userAddress.employee.municipality
			instance.administrativepost = userAddress.employee.administrativepost
			instance.village = userAddress.employee.village
			instance.save()
			messages.success(request, f'Inventáriu {instance.name} Adisiona ho Susesu.')
			return redirect('administration:inventoryList')
	else :
		form = InventoryForm()
	context = {
		"group":group,
		"title":"Adisiona Inventária",
		'inventoryActive':"active",
		'page':"add",
		'form':form,
	}
	return render(request, 'administration_layout/layout/inventoryForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def updateInventory(request, hashid):
	group = request.user.groups.all()[0].name
	inventoryData = get_object_or_404(Inventory, hashed=hashid)
	if request.method == "POST":
		form = InventoryForm(request.POST, instance=inventoryData)
		if form.is_valid():
			form.save()
			messages.success(request,f'Dadus Inventáriu Altera ho Susesu.')
			return redirect('administration:inventoryList')
	else :
		form = InventoryForm(instance=inventoryData)
	context = {
		"group":group,
		"title":"Update Inventária",
		'inventoryActive':"active",
		'page':"update",
		'form':form,
	}
	return render(request, 'administration_layout/layout/inventoryForm.html',context)

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def addUsedInventory(request):
	group = request.user.groups.all()[0].name
	userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
	availableInventory = Inventory.objects.filter(quantity__gt=0,village=userAddress.employee.village)
	if request.method == "POST":
		newid1 = getjustnewid(UsedInventory)
		newid2 = getjustnewid(UsedInventoryDetail)
		hashid1 = hash_md5(str(newid1))
		hashid2 = hash_md5(str(newid2))
		inventoryHashid = request.POST.get('inventory')
		inventory = get_object_or_404(Inventory,hashed=inventoryHashid)
		responsible = request.POST.get('responsible')
		used_date = request.POST.get('used_date')
		place = request.POST.get('place')
		user_created = User.objects.get(id=request.user.id)
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		quantity = request.POST.get('quantity')
		if int(quantity) > int(inventory.quantity):
			messages.success(request, f'Kuantidade Inventáriu nebe input, boot liu Kuantidade nebe iha sistema.')
			return redirect('administration:addUsedInventory')
		else:
			availableQuantity = int(inventory.quantity) - int(quantity)
			updateQuantity = Inventory.objects.filter(hashed=inventoryHashid).update(quantity=availableQuantity)
			usedInventory = UsedInventory.objects.create(id=newid1,user_created=user_created,\
							used_date=used_date,responsible=responsible,place=place,hashed=hashid1,municipality=userAddress.employee.municipality,\
							administrativepost=userAddress.employee.administrativepost,village=userAddress.employee.village)
			usedInventory.save()
			usedInventoryDetail = UsedInventoryDetail.objects.create(id=newid2,inventory=inventory,used=usedInventory,\
							user_created=user_created,quantity=quantity,hashed=hashid2,municipality=userAddress.employee.municipality,\
							administrativepost=userAddress.employee.administrativepost,village=userAddress.employee.village)
			usedInventoryDetail.save()
			messages.success(request, f'Inventáriu {inventory} Adisiona ona ba Inventáriu Uzadu ho Susesu.')
			return redirect('administration:usedInventoryList')
	context = {
		"group":group,
		"title":"Adisiona Inventária Uzadu",
		'usedInventoryActive':"active",
		'page':"add",
		'availableInventory':availableInventory,
	}
	return render(request, 'administration_layout/layout/usedInventoryForm.html',context)	

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def updateUsedInventory(request,hashid):
	group = request.user.groups.all()[0].name
	availableInventory = Inventory.objects.filter(quantity__gt=0)
	usedInventoryData = get_object_or_404(UsedInventoryDetail,hashed=hashid)
	usedInventoryHashid = usedInventoryData.used.hashed
	if request.method == "POST":
		inventoryHashid = request.POST.get('inventory')
		inventory = get_object_or_404(Inventory,hashed=inventoryHashid)
		responsible = request.POST.get('responsible')
		used_date = request.POST.get('used_date')
		place = request.POST.get('place')
		user_created = User.objects.get(id=request.user.id)
		quantity = request.POST.get('quantity')
		if int(quantity) != int(usedInventoryData.quantity):
			if int(quantity) > int(int(inventory.quantity) + int(usedInventoryData.quantity)):
				messages.success(request, f'Kuantidade Inventáriu nebe input, boot liu Kuantidade nebe iha sistema.')
				return redirect('administration:updateUsedInventory',hashid)
			else:
				availableQuantity = int(int(int(inventory.quantity) + int(usedInventoryData.quantity))) - int(quantity)
				updateQuantity = Inventory.objects.filter(hashed=inventoryHashid).update(quantity=availableQuantity)
				usedInventory = UsedInventory.objects.filter(hashed=usedInventoryHashid).update(used_date=used_date,responsible=responsible,place=place)
				usedInventoryDetail = UsedInventoryDetail.objects.filter(hashed=usedInventoryData.hashed).update(inventory=inventory,quantity=quantity)
				messages.success(request, f'Inventáriu Uzadu Altera ho Susesu.')
				return redirect('administration:usedInventoryList')
		else:
			usedInventory = UsedInventory.objects.filter(hashed=usedInventoryHashid).update(used_date=used_date,responsible=responsible,place=place)
			usedInventoryDetail = UsedInventoryDetail.objects.filter(hashed=usedInventoryData.hashed).update(inventory=inventory,used=usedInventory,\
							quantity=quantity)
			messages.success(request, f'Inventáriu Uzadu Altera ho Susesu.')
			return redirect('administration:usedInventoryList')
	context = {
		"group":group,
		"title":f"Update Inventária Uzadu : {usedInventoryData.inventory}",
		'usedInventoryActive':"active",
		'page':"update",
		'usedInventoryData':usedInventoryData,
		'availableInventory':availableInventory,
	}
	return render(request, 'administration_layout/layout/usedInventoryForm.html',context)	


@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def deleteInventory(request,hashid):
	inventory = get_object_or_404(Inventory,hashed=hashid)
	inventory_name = inventory.name
	inventory.delete()
	messages.error(request, f'Inventáriu {inventory_name} Hamoos ho Susesu.')
	return redirect('administration:inventoryList')

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def deleteUsedInventory(request,hashid):
	detailUsedInventory = get_object_or_404(UsedInventoryDetail,hashed=hashid)
	usedInventory = get_object_or_404(UsedInventory,hashed=detailUsedInventory.used.hashed)
	inventory = get_object_or_404(Inventory,hashed=detailUsedInventory.inventory.hashed)
	updateInventoryQuantity = int(inventory.quantity) + int(detailUsedInventory.quantity)
	updateInventory = Inventory.objects.filter(hashed=inventory.hashed).update(quantity=updateInventoryQuantity)
	detailUsedInventory.delete()
	messages.error(request, f'Dadus Inventáriu Uzadu {detailUsedInventory.inventory.name} Hamoos ho Susesu.')
	return redirect('administration:usedInventoryList')

@login_required
@allowed_users(allowed_roles=['sec','xefe'])
def allInventoryDataToExcel(request):
	userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
	response = HttpResponse(content_type='application/vnd.ms-excel')
	# response = HttpResponse(content_type='text/csv')
	# response['Content-Disposition'] = 'attachment; filename="Dadus Inventária - SIIGSA.csv"'
	response['Content-Disposition'] = 'attachment; filename="Dadus Inventária - SIIGSA.xls"'

	wb = xlwt.Workbook(encoding='utf-8')
	ws = wb.add_sheet(f'Livru Inventáriu Suku {userAddress.employee.village}')

	row_num = 0
	font_style = xlwt.XFStyle()
	font_style.font.bold = True

	columns = ['Naran Inventáriu','Data Sosa/Simu','Kondisaun','Nú Seri','Kuantidade','Folin Sosa','Fontes/Se mak fo','Marka','Se mak uza']

	for col_num in range(len(columns)):
		ws.write(row_num, col_num, columns[col_num], font_style)

	font_style = xlwt.XFStyle()
	rows = UsedInventoryDetail.objects.filter(village=userAddress.employee.village).values_list('inventory__name','inventory__recieve_date','inventory__condition','inventory__nu_serie','quantity',\
			'inventory__unitprice','inventory__supplier','inventory__brand','used__responsible')
	# rows.inventory.recieve_date.strftime('%d/%m/%Y')
	for row in rows:
		row_num += 1
		row[1].strftime('%d/%m/%Y')
		for col_num in range(len(row)):
			ws.write(row_num, col_num, row[col_num], font_style)

	wb.save(response)
	return response

@login_required
def exportInventory(request):
	import csv
	userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="A3. Livru Inventáriu Suku- SIIGSA.csv"'
	writer = csv.writer(response)
	columns = ['category','supplier','user_created','village','administrativepost','municipality','year','name','recieve_date','condition','nu_serie','quantity','unitprice','brand']
	rows = Inventory.objects.filter(village=userAddress.employee.village).values_list('category','supplier','village','administrativepost','municipality','year','name','recieve_date','condition','nu_serie','quantity','unitprice','brand')
	row_num = 0
	for row in rows:
		writer.writerow(row)
		row_num += 1
	return response

@login_required
def importInventory(request):
	import csv
	if request.method == "POST":
		inventoryCSVFiles = request.FILES.get('files')
		text_stream = io.TextIOWrapper(inventoryCSVFiles,encoding='utf-8')
		i = 0
		for row in csv.reader(text_stream):
			newid = getjustnewid(Inventory)
			hashid = hash_md5(str(newid))
			row.extend([newid,hashid])
			print("row:",row)
			user_created = get_object_or_404(User,request.user.id)
			village = get_object_or_404(Village,id=row[2])
			administrativepost = get_object_or_404(AdministrativePost,id=row[3])
			municipality = get_object_or_404(Municipality,id=row[4])
			year = get_object_or_404(Year,id=row[5])
			Inventory.objects.create(id=newid,hashed=hashid,category=row[0],supplier=row[1],user_created=user_created,village=village,administrativepost=administrativepost,municipality=municipality,year=year,name=row[6],recieve_date=row[7],condition=row[8],nu_serie=row[9],quantity=row[10],unitprice=row[11],brand=row[12])
			i = i+1
		messages.error(request, f'Total Dadus Inventáriu {i} mak Import ho Susesu.')
	context = {
		"title":"Import Dadus Suku",
	}
	return render(request, 'administration_layout/layout/importData.html',context)

@login_required
def exportUsedInventory(request):
	import csv
	userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="A3. Livru Inventáriu Uzadu Suku- SIIGSA.csv"'
	writer = csv.writer(response)
	rows = UsedInventory.objects.filter(village=userAddress.employee.village).values_list('village','administrativepost','municipality','used_date','responsible','place')
	row_num = 0
	for row in rows:
		writer.writerow(row)
		row_num += 1
	return response

@login_required
def importUsedInventory(request):
	import csv
	if request.method == "POST":
		inventoryCSVFiles = request.FILES.get('files')
		text_stream = io.TextIOWrapper(inventoryCSVFiles,encoding='utf-8')
		i = 0
		for row in csv.reader(text_stream):
			newid = getjustnewid(UsedInventory)
			hashid = hash_md5(str(newid))
			user_created = get_object_or_404(User,request.user.id)
			village = get_object_or_404(Village,id=row[0])
			administrativepost = get_object_or_404(AdministrativePost,id=row[1])
			municipality = get_object_or_404(Municipality,id=row[2])
			UsedInventory.objects.create(id=newid,hashed=hashid,user_created=user_created,village=village,administrativepost=administrativepost,municipality=municipality,used_date=row[3],responsible=row[4],place=row[5])
			i = i+1
		messages.error(request, f'Total Dadus Inventáriu Uzadu {i} mak Import ho Susesu.')
	context = {
		"title":"Import Dadus Suku",
	}
	return render(request, 'administration_layout/layout/importData.html',context)

@login_required
def exportUsedInventoryDetail(request):
	import csv
	userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="A3. Livru Detallu Inventáriu Uzadu Suku- SIIGSA.csv"'
	writer = csv.writer(response)
	rows = UsedInventoryDetail.objects.filter(village=userAddress.employee.village).values_list('inventory','used','village','administrativepost','municipality','quantity')
	row_num = 0
	for row in rows:
		writer.writerow(row)
		row_num += 1
	return response

@login_required
def importUsedInventoryDetail(request):
	import csv
	if request.method == "POST":
		inventoryCSVFiles = request.FILES.get('files')
		text_stream = io.TextIOWrapper(inventoryCSVFiles,encoding='utf-8')
		i = 0
		for row in csv.reader(text_stream):
			newid = getjustnewid(UsedInventoryDetail)
			hashid = hash_md5(str(newid))
			user_created = get_object_or_404(User,request.user.id)
			village = get_object_or_404(Village,id=row[2])
			administrativepost = get_object_or_404(AdministrativePost,id=row[3])
			municipality = get_object_or_404(Municipality,id=row[4])
			UsedInventoryDetail.objects.create(id=newid,hashed=hashid,user_created=user_created,village=village,administrativepost=administrativepost,municipality=municipality,inventory=row[0],used=row[1],quantity=row[5])
			i = i+1
		messages.error(request, f'Total Dadus Detallu Inventáriu Uzadu {i} mak Import ho Susesu.')
	context = {
		"title":"Import Dadus Suku",
	}
	return render(request, 'administration_layout/layout/importData.html',context)
