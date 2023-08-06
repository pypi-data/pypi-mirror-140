from django.shortcuts import render,redirect, get_object_or_404,HttpResponse
from django.http import JsonResponse
from django.contrib import messages
from ..forms import *
from ..models import *
from employee.models import *
from django.contrib.auth.models import User
from custom.utils import *
from django.db.models import Count
# pdf library
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.auth.decorators import login_required
from datetime import date
# Create your views here.
@login_required
def administrationDashboard(request):
	currentYear = date.today().year
	currentYear = get_object_or_404(Year,year=currentYear)
	if request.user.groups.all()[0].name == "admin":
		countLetterOut = LetterOut.objects.filter(year=currentYear).count()
		countLetterIn = LetterIn.objects.filter(year=currentYear).count()
		countComplaint = Complaint.objects.filter(year=currentYear).count()
		countVisitor = Visitor.objects.filter(year=currentYear).count()
		countDecision = Decision.objects.filter(year=currentYear).count()
		countInventory = Inventory.objects.filter(year=currentYear).count()
	else :
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		countLetterOut = LetterOut.objects.filter(year=currentYear,village=userAddress.employee.village).count()
		countLetterIn = LetterIn.objects.filter(year=currentYear,village=userAddress.employee.village).count()
		countComplaint = Complaint.objects.filter(year=currentYear,village=userAddress.employee.village).count()
		countVisitor = Visitor.objects.filter(year=currentYear,village=userAddress.employee.village).count()
		countDecision = Decision.objects.filter(year=currentYear,village=userAddress.employee.village).count()
		countInventory = Inventory.objects.filter(year=currentYear,village=userAddress.employee.village).count()
	context = {
		'title':"A. LIVRU ADMINISTRASAUN PÚBLIKU",
		'homeActive':"active",
		'countLetterOut':countLetterOut,
		'countLetterIn':countLetterIn,
		'countComplaint':countComplaint,
		'countVisitor':countVisitor,
		'countDecision':countDecision,
		'countInventory':countInventory,
		'currentYear': date.today().year,
	}
	return render(request,"administration_layout/main/dashboard.html",context)

# ===================charts===================
def convertMonthNumberToText(number):
	if number == 1:
		return "Janeiru"
	elif number == 2:
		return "Fevreiru"
	elif number == 3:
		return "Marsu"
	elif number == 4:
		return "Abril"
	elif number == 5:
		return "Maiu"
	elif number == 6:
		return "Junhu"
	elif number == 7:
		return "Julhu"
	elif number == 8:
		return "Augustu"
	elif number == 9:
		return "Setembru"
	elif number == 10:
		return "Outubru"
	elif number == 11:
		return "Novembru"
	elif number == 12:
		return "Dezembru"
	

@login_required
def letterin_charts(request):
	currentYear = date.today().year
	labels = []
	data = []
	currentYear = get_object_or_404(Year,year=currentYear)
	if request.user.groups.all()[0].name == "admin":
		querysets = LetterIn.objects.filter(year=currentYear).values('letter_date__month').annotate(count=Count('id'))
	else :
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		querysets = LetterIn.objects.filter(year=currentYear,village=userAddress.employee.village).values('letter_date__month').annotate(count=Count('id')).order_by('letter_date__month')
	for entry in querysets:
		month = convertMonthNumberToText(entry['letter_date__month'])
		labels.append(month)
		data.append(entry['count'])
	return JsonResponse(data={
		'labels':labels,'data':data,
		})

@login_required
def letterinbyyear_charts(request):
	labels = []
	data = []
	if request.user.groups.all()[0].name == "admin":
		querysets = LetterIn.objects.values('letter_date__year').annotate(count=Count('id')).order_by('letter_date__year')
	else :
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		querysets = LetterIn.objects.filter(village=userAddress.employee.village).values('letter_date__year').annotate(count=Count('id')).order_by('letter_date__year')
	for entry in querysets:
		labels.append(entry['letter_date__year'])
		data.append(entry['count'])
	return JsonResponse(data={
		'labels':labels,'data':data,
		})

@login_required
def letterout_charts(request):
	currentYear = date.today().year
	labels = []
	data = []
	currentYear = get_object_or_404(Year,year=currentYear)
	if request.user.groups.all()[0].name == "admin":
		querysets = LetterOut.objects.filter(year=currentYear).values('letter_date__month').annotate(count=Count('id')).order_by('letter_date__month')
	else :
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		querysets = LetterOut.objects.filter(year=currentYear,village=userAddress.employee.village).values('letter_date__month').annotate(count=Count('id')).order_by('letter_date__month')
	for entry in querysets:
		month = convertMonthNumberToText(entry['letter_date__month'])
		labels.append(month)
		data.append(entry['count'])
	return JsonResponse(data={
		'labels':labels,'data':data,
		})

@login_required
def letteroutbyyear_charts(request):
	labels = []
	data = []
	if request.user.groups.all()[0].name == "admin":
		querysets = LetterOut.objects.values('letter_date__year').annotate(count=Count('id')).order_by('letter_date__year')
	else :
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		querysets = LetterOut.objects.filter(village=userAddress.employee.village).values('letter_date__year').annotate(count=Count('id')).order_by('letter_date__year')
	for entry in querysets:
		labels.append(entry['letter_date__year'])
		data.append(entry['count'])
	return JsonResponse(data={
		'labels':labels,'data':data,
		})

@login_required
def complaint_charts(request):
	currentYear = date.today().year
	labels = []
	data = []
	currentYear = get_object_or_404(Year,year=currentYear)
	if request.user.groups.all()[0].name == "admin":
		querysets = Complaint.objects.filter(year=currentYear).values('date__month').annotate(count=Count('id'))
	else :
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		querysets = Complaint.objects.filter(year=currentYear,village=userAddress.employee.village).values('date__month').annotate(count=Count('id'))
	for entry in querysets:
		month = convertMonthNumberToText(entry['date__month'])
		labels.append(month)
		data.append(entry['count'])
	return JsonResponse(data={
		'labels':labels,'data':data,
		})

@login_required
def complaintbyyear_charts(request):
	labels = []
	data = []
	if request.user.groups.all()[0].name == "admin":
		querysets = Complaint.objects.values('date__year').annotate(count=Count('id')).order_by('date__year')
	else :
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		querysets = Complaint.objects.filter(village=userAddress.employee.village).values('date__year').annotate(count=Count('id')).order_by('date__year')
	for entry in querysets:
		labels.append(entry['date__year'])
		data.append(entry['count'])
	return JsonResponse(data={
		'labels':labels,'data':data,
		})

@login_required
def visitor_charts(request):
	currentYear = date.today().year
	labels = []
	data = []
	currentYear = get_object_or_404(Year,year=currentYear)
	if request.user.groups.all()[0].name == "admin":
		querysets = Visitor.objects.filter(year=currentYear).values('visitDate__month').annotate(count=Count('id'))
	else :
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		querysets = Visitor.objects.filter(year=currentYear,village=userAddress.employee.village).values('visitDate__month').annotate(count=Count('id'))
	for entry in querysets:
		month = convertMonthNumberToText(entry['visitDate__month'])
		labels.append(month)
		data.append(entry['count'])
	return JsonResponse(data={
		'labels':labels,'data':data,
		})

@login_required
def visitorbyyear_charts(request):
	labels = []
	data = []
	if request.user.groups.all()[0].name == "admin":
		querysets = Visitor.objects.values('visitDate__year').annotate(count=Count('id')).order_by('visitDate__year')
	else :
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		querysets = Visitor.objects.filter(village=userAddress.employee.village).values('visitDate__year').annotate(count=Count('id')).order_by('visitDate__year')
	for entry in querysets:
		labels.append(entry['visitDate__year'])
		data.append(entry['count'])
	return JsonResponse(data={
		'labels':labels,'data':data,
		})

# @login_required
# def complaint_charts(request):
# 	currentYear = date.today().year
# 	labels = []
# 	data = []
# 	currentYear = get_object_or_404(Year,year=currentYear)
# 	if request.user.groups.all()[0].name == "admin":
# 		querysets = Complaint.objects.filter(year=currentYear).values('date__month').annotate(count=Count('id'))
# 	else :
# 		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
# 		querysets = Complaint.objects.filter(year=currentYear,village=userAddress.employee.village).values('date__month').annotate(count=Count('id'))
# 	for entry in querysets:
# 		month = convertMonthNumberToText(entry['date__month'])
# 		labels.append(month)
# 		data.append(entry['count'])

# 	return JsonResponse(data={
# 		'labels':labels,
# 		'data':data,
# 		})

@login_required
def inventory_charts(request):
	currentYear = date.today().year
	labels = []
	data = []
	currentYear = get_object_or_404(Year,year=currentYear)
	if request.user.groups.all()[0].name == "admin":
		querysets = Inventory.objects.filter(year=currentYear).values('category').annotate(count=Count('id'))
	else :
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		querysets = Inventory.objects.filter(year=currentYear,village=userAddress.employee.village).values('category').annotate(count=Count('id'))
	for entry in querysets:
		labels.append(entry['category'])
		data.append(entry['count'])
	return JsonResponse(data={
		'labels':labels,'data':data,
		})

@login_required
def inventoryall_charts(request):
	labels = []
	data = []
	if request.user.groups.all()[0].name == "admin":
		querysets = Inventory.objects.values('category').annotate(count=Count('id'))
	else :
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		querysets = Inventory.objects.filter(village=userAddress.employee.village).values('category').annotate(count=Count('id'))
	for entry in querysets:
		labels.append(entry['category'])
		data.append(entry['count'])
	return JsonResponse(data={
		'labels':labels,'data':data,
		})

@login_required
def decision_charts(request):
	currentYear = date.today().year
	labels = []
	data = []
	currentYear = get_object_or_404(Year,year=currentYear)
	if request.user.groups.all()[0].name == "admin":
		querysets = Decision.objects.filter(year=currentYear).values('decision_type').annotate(count=Count('decision_type'))
	else :
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		querysets = Decision.objects.filter(year=currentYear,village=userAddress.employee.village).values('decision_type').annotate(count=Count('decision_type'))
	for entry in querysets:
		labels.append(entry['decision_type'])
		data.append(entry['count'])
	return JsonResponse(data={
		'labels':labels,'data':data,
		})

@login_required
def decisionall_charts(request):
	labels = []
	data = []
	if request.user.groups.all()[0].name == "admin":
		querysets = Decision.objects.values('decision_type').annotate(count=Count('decision_type'))
	else :
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		querysets = Decision.objects.filter(village=userAddress.employee.village).values('decision_type').annotate(count=Count('decision_type'))
	for entry in querysets:
		labels.append(entry['decision_type'])
		data.append(entry['count'])
	return JsonResponse(data={
		'labels':labels,'data':data,
		})

# ====================Report====================
@login_required
def administration_report(request):
	tinan = Year.objects.all()
	if request.method == "POST":
		administrationReport = request.POST.get('administrationReport')
		year = request.POST.get('year')
		year = get_object_or_404(Year,year=year)
		if administrationReport == "A1":
			decision_type = "Konsellu Suku"
			count_villageAdvise = CommunityLeadership.objects.filter(status="Yes").count()
			if request.user.groups.all()[0].name == "admin":
				userAddress = ""
				decisionlist = Decision.objects.filter(year=year,decision_type=decision_type)
			else:
				userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
				decisionlist = Decision.objects.filter(year=year,decision_type=decision_type,village=userAddress.employee.village)
				totalDecision = Decision.objects.filter(year=year,decision_type=decision_type,village=userAddress.employee.village).count()
			data = {'totalDecision':totalDecision,'userAddress':userAddress,'year':year,'decision_type':decision_type,'count_villageAdvise':count_villageAdvise,'decisionlist':decisionlist,'year':year,"title":"PDF Desizaun Konsellu Suku"}
			if 'print' in request.POST:
				data["page"] = "print"
				return render(request,"administration_layout/report/A1_report.html",data)
			elif 'excel' in request.POST:
				data["page"] = "excel"
				return render(request,"administration_layout/report/A1_report.html",data)
			elif 'pdf' in request.POST:
				pdf = render_to_pdf('administration_layout/pdf/pdf_desizaun_konsellu_suku.html', data)
				return HttpResponse(pdf, content_type='application/pdf')

		if administrationReport == "A2":
			decision_type = "Xefe Suku"
			count_villageAdvise = CommunityLeadership.objects.filter(status="Yes").count()
			if request.user.groups.all()[0].name == "admin":
				userAddress = ""
				decisionlist = Decision.objects.filter(year=year,decision_type=decision_type)
			else:
				userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
				decisionlist = Decision.objects.filter(year=year,decision_type=decision_type,village=userAddress.employee.village)
				totalDecision = Decision.objects.filter(year=year,decision_type=decision_type,village=userAddress.employee.village).count()
			data ={'totalDecision':totalDecision,'userAddress':userAddress,'year':year,'decision_type':decision_type,'count_villageAdvise':count_villageAdvise,'decisionlist':decisionlist,'year':year,"title":"PDF Desizaun Xefe Suku"}
			if 'print' in request.POST:
				data["page"] = "print"
				return render(request,"administration_layout/report/A2_report.html",data)
			elif 'excel' in request.POST:
				data["page"] = "excel"
				return render(request,"administration_layout/report/A2_report.html",data)
			elif 'pdf' in request.POST:
				pdf = render_to_pdf('administration_layout/pdf/pdf_desizaun_xefe_suku.html', data)
				return HttpResponse(pdf, content_type='application/pdf')

		if administrationReport == "A3":
			if request.user.groups.all()[0].name == "admin":
				userAddress = ""
				inventoryList = UsedInventoryDetail.objects.filter(inventory__year=year)
			else:
				userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
				inventoryList = UsedInventoryDetail.objects.filter(inventory__year=year,village=userAddress.employee.village)
				TotalInventory = UsedInventoryDetail.objects.filter(inventory__year=year,village=userAddress.employee.village).count()
			data ={'TotalInventory':TotalInventory,'userAddress':userAddress,'inventoryList':inventoryList,'year':year,"title":"PDF Livru Inventariu Suku"}
			if 'print' in request.POST:
				data["page"] = "print"
				return render(request,"administration_layout/report/A3_report.html",data)
			elif 'excel' in request.POST:
				data["page"] = "excel"
				return render(request,"administration_layout/report/A3_report.html",data)
			elif 'pdf' in request.POST:
				pdf = render_to_pdf('administration_layout/pdf/pdf_livru_inventariu_suku.html', data)
				return HttpResponse(pdf, content_type='application/pdf')

		if administrationReport == "A4":
			if request.user.groups.all()[0].name == "admin":
				userAddress = ""
				letterOutList = LetterOut.objects.filter(year=year)
			else :
				userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
				letterOutList = LetterOut.objects.filter(year=year,village=userAddress.employee.village)
				totalLetterOutList = LetterOut.objects.filter(year=year,village=userAddress.employee.village).count()
			data ={'totalLetterOutList':totalLetterOutList,'userAddress':userAddress,'letterOutList':letterOutList,'year':year,"title":"PDF Livru Ajenda Surat Sai"}
			if 'print' in request.POST:
				data["page"] = "print"
				return render(request,"administration_layout/report/A4_report.html",data)
			elif 'excel' in request.POST:
				data["page"] = "excel"
				return render(request,"administration_layout/report/A4_report.html",data)
			elif 'pdf' in request.POST:
				pdf = render_to_pdf('administration_layout/pdf/pdf_livru_ajenda_surat_sai.html', data)
				return HttpResponse(pdf, content_type='application/pdf')
			
		if administrationReport == "A5":
			if request.user.groups.all()[0].name == "admin":
				userAddress = ""
				letterInList = LetterIn.objects.filter(year=year)
			else :
				userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
				letterInList = LetterIn.objects.filter(year=year,village=userAddress.employee.village)
				totalLetterInList = LetterIn.objects.filter(year=year,village=userAddress.employee.village).count()
			data ={'totalLetterInList':totalLetterInList,'userAddress':userAddress,'letterInList':letterInList,'year':year,"title":"PDF Livru Ajenda Surat Tama"}
			if 'print' in request.POST:
				data["page"] = "print"
				return render(request,"administration_layout/report/A5_report.html",data)
			elif 'excel' in request.POST:
				data["page"] = "excel"
				return render(request,"administration_layout/report/A5_report.html",data)
			elif 'pdf' in request.POST:
				pdf = render_to_pdf('administration_layout/pdf/pdf_livru_ajenda_surat_tama.html', data)
				return HttpResponse(pdf, content_type='application/pdf')

		if administrationReport == "A6":
			if request.user.groups.all()[0].name == "admin":
				userAddress = ""
				expeditionList = LetterOutExpedition.objects.filter(letter_out__year=year)
			else :
				userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
				expeditionList = LetterOutExpedition.objects.filter(letter_out__year=year,village=userAddress.employee.village)
				totalExpeditionList = LetterOutExpedition.objects.filter(letter_out__year=year,village=userAddress.employee.village).count()
			data ={'totalExpeditionList':totalExpeditionList,'userAddress':userAddress,'expeditionList':expeditionList,'year':year,"title":"PDF Livru Espedisaun"}
			if 'print' in request.POST:
				data["page"] = "print"
				return render(request,"administration_layout/report/A6_report.html",data)
			if 'excel' in request.POST:
				data["page"] = "excel"
				return render(request,"administration_layout/report/A6_report.html",data)
			elif 'pdf' in request.POST:
				pdf = render_to_pdf('administration_layout/pdf/pdf_livru_espedisaun.html', data)
				return HttpResponse(pdf, content_type='application/pdf')

		if administrationReport == "A7":
			if request.user.groups.all()[0].name == "admin":
				userAddress = ""
				commLeadershipList = CommunityLeadership.objects.filter(year=year,status="Yes")
			else :
				userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
				commLeadershipList = CommunityLeadership.objects.filter(year=year,status="Yes",village=userAddress.employee.village).order_by('position')
				totalCommLeadershipList = CommunityLeadership.objects.filter(year=year,status="Yes",village=userAddress.employee.village).count()
			data ={'totalCommLeadershipList':totalCommLeadershipList,'userAddress':userAddress,'commLeadershipList':commLeadershipList,'year':year,"title":"PDF Livru Lideransa Komunitaria"}
			if 'print' in request.POST:
				data["page"] = "print"
				return render(request,"administration_layout/report/A7_report.html",data)
			if 'excel' in request.POST:
				data["page"] = "excel"
				return render(request,"administration_layout/report/A7_report.html",data)
			elif 'pdf' in request.POST:
				pdf = render_to_pdf('administration_layout/pdf/pdf_livru_lideransa_komunitariu.html', data)
				return HttpResponse(pdf, content_type='application/pdf')
			
		if administrationReport == "A10":
			if request.user.groups.all()[0].name == "admin":
				userAddress = ""
				ComplaintList = Complaint.objects.filter(year=year)
			else :
				userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
				ComplaintList = Complaint.objects.filter(year=year,village=userAddress.employee.village)
				totalComplaintList = Complaint.objects.filter(year=year,village=userAddress.employee.village).count()
			data ={'totalComplaintList':totalComplaintList,'userAddress':userAddress,'ComplaintList':ComplaintList,'year':year,"title":"PDF Rejistu Keixa Suku"}
			if 'print' in request.POST:
				data["page"] = "print"
				return render(request,"administration_layout/report/A10_report.html",data)
			if 'excel' in request.POST:
				data["page"] = "excel"
				return render(request,"administration_layout/report/A10_report.html",data)
			elif 'pdf' in request.POST:
				pdf = render_to_pdf('administration_layout/pdf/pdf_rejistu_keixa_suku.html', data)
				return HttpResponse(pdf, content_type='application/pdf')

		if administrationReport == "A11":
			if request.user.groups.all()[0].name == "admin":
				userAddress = ""
				VisitorList = Visitor.objects.filter(year=year)
			else :
				userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
				VisitorList = Visitor.objects.filter(year=year,village=userAddress.employee.village)
				totalVisitorList = Visitor.objects.filter(year=year,village=userAddress.employee.village).count()
			data ={'totalVisitorList':totalVisitorList,'userAddress':userAddress,'VisitorList':VisitorList,'year':year,"title":"PDF Rejistu Bainaka Suku"}
			if 'print' in request.POST:
				data["page"] = "print"
				return render(request,"administration_layout/report/A11_report.html",data)
			if 'excel' in request.POST:
				data["page"] = "excel"
				return render(request,"administration_layout/report/A11_report.html",data)
			elif 'pdf' in request.POST:
				pdf = render_to_pdf('administration_layout/pdf/pdf_rejistu_bainaka_suku.html', data)
				return HttpResponse(pdf, content_type='application/pdf')
			
	context = {
		'title':"Livru Relatóriu Sira",
		'reportActive':"active",
		'tinan':tinan,
	}
	return render(request,"administration_layout/layout/administration_report.html",context)


#========================= all pdf functions============================
@login_required
def pdfMinutaEnkontruSuku(request,hashid):
	if request.user.groups.all()[0].name == "admin":
		userAddress = ''
		meetingData = get_object_or_404(MeetingTime,hashed=hashid)
		meetingDecision = get_object_or_404(Decision,hashed=meetingData.decision.hashed)
		villageAdviseAbsentInDecision = DecisionDetail.objects.filter(decision__hashed=meetingDecision.hashed,attendance="No")
	else:
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		meetingData = get_object_or_404(MeetingTime,hashed=hashid)
		meetingDecision = get_object_or_404(Decision,hashed=meetingData.decision.hashed)
		villageAdviseAbsentInDecision = DecisionDetail.objects.filter(decision__hashed=meetingDecision.hashed,attendance="No")
	data ={"userAddress":userAddress,'meetingData':meetingData,'meetingDetail':villageAdviseAbsentInDecision,"title":"PDF Minutas Enkontru Suku"}
	pdf = render_to_pdf('administration_layout/pdf/pdf_minuta_enkontru_suku.html', data)
	return HttpResponse(pdf, content_type='application/pdf')

@login_required
def printMinutaEnkontruSuku(request,hashid):
	if request.user.groups.all()[0].name == "admin":
		userAddress = ''
		meetingData = get_object_or_404(MeetingTime,hashed=hashid)
		meetingDecision = get_object_or_404(Decision,hashed=meetingData.decision.hashed)
		villageAdviseAbsentInDecision = DecisionDetail.objects.filter(decision__hashed=meetingDecision.hashed,attendance="No")
	else:
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		meetingData = get_object_or_404(MeetingTime,hashed=hashid)
		meetingDecision = get_object_or_404(Decision,hashed=meetingData.decision.hashed)
		villageAdviseAbsentInDecision = DecisionDetail.objects.filter(decision__hashed=meetingDecision.hashed,attendance="No")
	data ={"userAddress":userAddress,'meetingData':meetingData,'meetingDetail':villageAdviseAbsentInDecision,"title":"Print Minutas Enkontru Suku"}
	return render(request,"administration_layout/report/A9_report.html",data)

@login_required
def pdfMeetingAttendance(request,hashid):
	if request.user.groups.all()[0].name == "admin":
		decision = get_object_or_404(Decision,hashed=hashid)
		attendance = []
		otherList = Attendance.objects.filter(decision=decision)
		villageAdviseAttendance = DecisionDetail.objects.filter(decision=decision,attendance="Yes")
	else:
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		decision = get_object_or_404(Decision,hashed=hashid)
		attendance = []
		otherList = Attendance.objects.filter(decision=decision,village=userAddress.employee.village)
		villageAdviseAttendance = DecisionDetail.objects.filter(decision=decision,attendance="Yes")
	for i in villageAdviseAttendance.iterator():
		attendance.append({
			"naran":i.villageAdvise.population.name,
			"instituition":"Konsellu Suku",
			"position":i.villageAdvise.position,
			"asinatura":""
		})
	for i in otherList.iterator():
		attendance.append({
			"naran":i.name,
			"instituition":i.instituition,
			"position":i.position,
			"asinatura":""
		})
	data ={"decision":decision,"attendanceList":attendance,"title":"Print Lista Prezensa Suku"}
	pdf = render_to_pdf('administration_layout/pdf/pdf_lista_prezensa.html', data)
	return HttpResponse(pdf, content_type='application/pdf')

@login_required
def printMeetingAttendance(request,hashid):
	if request.user.groups.all()[0].name == "admin":
		decision = get_object_or_404(Decision,hashed=hashid)
		attendance = []
		otherList = Attendance.objects.filter(decision=decision)
		villageAdviseAttendance = DecisionDetail.objects.filter(decision=decision,attendance="Yes")
	else:
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		decision = get_object_or_404(Decision,hashed=hashid)
		attendance = []
		otherList = Attendance.objects.filter(decision=decision)
		villageAdviseAttendance = DecisionDetail.objects.filter(decision=decision,attendance="Yes")
	for i in villageAdviseAttendance.iterator():
		if i.villageAdvise.population.gender == "m":
			sex = "Mane"
		elif i.villageAdvise.population.gender == "f":
			sex = "Feto"
		elif i.villageAdvise.population.gender == "s":
			sex = "Seluk"
		attendance.append({
			"naran":i.villageAdvise.population.name,
			"sex":sex,
			"instituition":"Konsellu Suku",
			"position":i.villageAdvise.position,
			"deficient":i.villageAdvise.population.deficient,
			"asinatura":""
		})
	for i in otherList.iterator():
		attendance.append({
			"naran":i.name,
			"sex":i.sex,
			"instituition":i.instituition,
			"position":i.position,
			"deficient":i.deficient,
			"asinatura":""
		})
	data ={"decision":decision,"attendanceList":attendance,"title":"Print Lista Prezensa Suku"} 
	return render(request,"administration_layout/report/A8_report.html",data)

@login_required
def printCommunityLeadershipHistory(request,hashid):
	if request.user.groups.all()[0].name == "admin":
		userAddress = ""
		period = get_object_or_404(MandatePeriod,id=hashid)
		communityLeadershipList = CommunityLeadership.objects.filter(period=period,status="No").order_by('-id')
	else:
		userAddress = get_object_or_404(EmployeeUser,user__id=request.user.id)
		period = get_object_or_404(MandatePeriod,id=hashid)
		communityLeadershipList = CommunityLeadership.objects.filter(period=period,status="No",village=userAddress.employee.village).order_by('-id')
	data ={"userAddress":userAddress,"period":period,"communityLeadershipList":communityLeadershipList,"title":f"Print Lista Lideransa Comunitaria {period}"} 
	return render(request,"administration_layout/report/A7a_report.html",data)

@login_required
def printDecisioResult(request,hashid):
	decision_type = "Konsellu Suku"
	decision = get_object_or_404(Decision,decision_type="Konsellu Suku",hashed=hashid)
	data ={"decision_type":decision_type,"decision":decision,"title":f"Print Detaillu Desizaun Konsellu Suku"} 
	return render(request,"administration_layout/report/A1a_report.html",data)

@login_required
def printDecisioResult1(request,hashid):
	decision_type = "Xefe Suku"
	decision = get_object_or_404(Decision,decision_type="Xefe Suku",hashed=hashid)
	data ={"decision_type":decision_type,"decision":decision,"title":f"Print Detaillu Desizaun Xefe Suku"} 
	return render(request,"administration_layout/report/A2a_report.html",data)


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
