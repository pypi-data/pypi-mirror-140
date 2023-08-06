from django.urls import path
from .views import *
app_name = 'administration'
urlpatterns =[
	path('',administrationDashboard,name="administrationDashboard"),
	path('Relatorio-Livru-Administrasaun/',administration_report,name="administration_report"),
	path('Relatorio-Minuta-Enkontru-PDF/<str:hashid>',pdfMinutaEnkontruSuku,name="pdfMinutaEnkontruSuku"),
	path('Relatorio-Minuta-Enkontru-Print/<str:hashid>',printMinutaEnkontruSuku,name="printMinutaEnkontruSuku"),
	path('Relatorio-Lista-Prezensa-Enkontru-Print/<str:hashid>',printMeetingAttendance,name="printMeetingAttendance"),
	path('Relatorio-Lista-Prezensa-Enkontru-PDF/<str:hashid>',pdfMeetingAttendance,name="pdfMeetingAttendance"),
	path('Print-Resultadu-Desizaun-Enkontru-Konsellu-Suku/<str:hashid>',printDecisioResult,name="printDecisioResult"),
	path('Print-Resultadu-Desizaun-Enkontru-Xefe-Suku/<str:hashid>',printDecisioResult1,name="printDecisioResult1"),


	
	path('desizaun-konsellu-suku/', villageAdviseDecisionList, name="villageAdviseDecisionList"),
	path('Add-desizaun-konsellu-suku/', addDecisionVillageAdvise, name="addDecisionVillageAdvise"),
	path('Update-desizaun-konsellu-suku/<str:hashid>', updateDecisionVillageAdvise, name="updateDecisionVillageAdvise"),
	path('View-desizaun-konsellu-suku/<str:hashid>', viewDecisionVillageAdvise, name="viewDecisionVillageAdvise"),
	path('Delete-desizaun-konsellu-suku/<str:hashid>', deleteDecisionVillageAdvise, name="deleteDecisionVillageAdvise"),
	path('Add-Rezultadu-desizaun-konsellu-suku/<str:decisionHashid>', addDecisionResult, name="addDecisionResult"),
	path('Update-Rezultadu-desizaun-konsellu-suku/<str:hashid>/<str:decision>', updateVotingResult, name="updateVotingResult"),
	path('Delete-Rezultadu-desizaun-konsellu-suku/<str:hashid>/<str:decision>', deleteVotingResult, name="deleteVotingResult"),
	
	path('desizaun-xefe-suku/', villageChiefDecisionList, name="villageChiefDecisionList"),
	path('Add-desizaun-xefe-suku/', addDecisionVillageChief, name="addDecisionVillageChief"),
	path('Update-desizaun-xefe-suku/<str:hashid>', updateDecisionVillageChief, name="updateDecisionVillageChief"),
	path('View-desizaun-xefe-suku/<str:hashid>', viewDecisionVillageChief, name="viewDecisionVillageChief"),
	path('Delete-desizaun-xefe-suku/<str:hashid>', deleteDecisionVillageChief, name="deleteDecisionVillageChief"),
	path('Update-Rezultadu-desizaun-Xefe-suku/<str:hashid>/<str:decision>', updateVotingResult1, name="updateVotingResult1"),
	path('Add-Rezultadu-desizaun-Xefe-suku/<str:decisionHashid>', addDecisionResult1, name="addDecisionResult1"),
	path('Delete-Rezultadu-desizaun-Xefe-suku/<str:hashid>/<str:decision>', deleteVotingResult1, name="deleteVotingResult1"),
	

	path('Periodu-Mandatu/', periodList, name="periodList"),
	path('Add-Periodu-Mandatu/', addPeriod, name="addPeriod"),
	path('Update-Periodu-Mandatu/<str:hashid>', updatePeriod, name="updatePeriod"),
	path('Delete-Periodu-Mandatu/<str:hashid>', deletePeriod, name="deletePeriod"),
	path('Dadus-Lideransa-Komunitaria-Periodu/<str:hashid>', detailPeriod, name="detailPeriod"),
	path('ajax/load-populasaun/', load_populations, name='load_populations'),
	path('ajax/load-aldeia/', load_aldeia, name='load_aldeia'),

	path('lideransa-komunitaria/', communityLeadershipList, name="communityLeadershipList"),
	path('Add-lideransa-komunitaria/', addCommunityLidership, name="addCommunityLidership"),
	path('Add-lideransa-komunitaria-Xefe-aldeia/', addCommunityLidershipAldeia, name="addCommunityLidershipAldeia"),
	path('Update-lideransa-komunitaria/<str:hashid>', updateCommunityLidership, name="updateCommunityLidership"),
	path('Delete-lideransa-komunitaria/<str:hashid>', deleteCommunityLeadership, name="deleteCommunityLeadership"),
	path('View-lideransa-komunitaria/<str:hashid>', viewCommunityLeadership, name="viewCommunityLeadership"),
	path('Change-lideransa-komunitaria/<str:hashidPreviousLeader>', changeCommunityLeadership, name="changeCommunityLeadership"),
	path('Termina-lideransa-komunitaria/<str:hashid>', terminateCommunityLeadership, name="terminateCommunityLeadership"),
	path('Print-lideransa-komunitaria-periodu/<str:hashid>', printCommunityLeadershipHistory, name="printCommunityLeadershipHistory"),
	path('Lista-Kargu/', positionList, name="positionList"),
	path('Add-Kargu/', addPosition, name="addPosition"),
	path('Update-Kargu/<str:hashid>', updatePosition, name="updatePosition"),
	path('Delete-Kargu/<str:hashid>', deletePosition, name="deletePosition"),
	
	path('Keixa/', complaintList, name="complaintList"),
	path('Add-Keixa/', addComplaint, name="addComplaint"),
	path('Update-Keixa/<str:hashid>', updateComplaint, name="updateComplaint"),
	path('Delete-Keixa/<str:hashid>', deleteComplaint, name="deleteComplaint"),
	
	# Letter In & Out
	path('Surat-Tama/', letterInList, name="letterInList"),
	path('Add-Surat-Tama/', addLetterIn, name="addLetterIn"),
	path('Update-Surat-Tama/<str:hashid>', updateLetterIn, name="updateLetterIn"),
	path('Delete-Surat-Tama/<str:hashid>', deleteLetterIn, name="deleteLetterIn"),
	path('Surat-Sai/', letterOutList, name="letterOutList"),
	path('Add-Surat-Sai/', addLetterOut, name="addLetterOut"),
	path('Update-Surat-Sai/<str:hashid>', updateLetterOut, name="updateLetterOut"),
	path('Delete-Surat-Sai/<str:hashid>', deleteLetterOut, name="deleteLetterOut"),
	path('Expedisaun/', expeditionList, name="expeditionList"),
	path('Add-Expedisaun/<str:hashid>', addExpedition, name="addExpedition"),
	path('View-Detaillu-Expedisaun/<str:hashid>', viewExpeditionDetail, name="viewExpeditionDetail"),
	path('Upload-File-Aneksu-Expedisaun/<str:hashid>', uploadExpeditionFile, name="uploadExpeditionFile"),
	path('Update-File-Aneksu-Expedisaun/<str:hashid>', updateFileExpedition, name="updateFileExpedition"),
	path('Update-Expedisaun/<str:hashid>', updateExpedition, name="updateExpedition"),
	path('Delete-Expedisaun/<str:hashid>', deleteExpedition, name="deleteExpedition"),
	
	# inventory
	path('Lista-Inventaria/', inventoryList, name="inventoryList"),
	path('Add-Inventaria/', addInventory, name="addInventory"),
	path('Update-Inventaria/<str:hashid>', updateInventory, name="updateInventory"),
	path('Lista-Inventaria-Uzadu/', usedInventoryList, name="usedInventoryList"),
	path('Add-Inventaria-Uzadu/', addUsedInventory, name="addUsedInventory"),
	path('Update-Inventaria-Uzadu/<str:hashid>', updateUsedInventory, name="updateUsedInventory"),
	path('Delete-Inventaria/<str:hashid>', deleteInventory, name="deleteInventory"),
	path('Delete-Used-Inventaria/<str:hashid>', deleteUsedInventory, name="deleteUsedInventory"),
	
	#meetings
	path('Lista-Minuta-Enkontru-Suku/', meetingList, name="meetingList"),
	path('Add-Minuta-Enkontru-Suku/<str:decisionId>/', addMeeting, name="addMeeting"),
	path('View-Minuta-Enkontru-Suku/<str:hashid>/', viewMeetingMinutes, name="viewMeetingMinutes"),
	path('Update-Minuta-Enkontru-Suku/<str:hashid>/', updateMeetingMinutes, name="updateMeetingMinutes"),
	path('Delete-Minuta-Enkontru-Suku/<str:hashid>/', deleteMeetingMinutes, name="deleteMeetingMinutes"),

	#visitor
	path('Lista-Bainaka-Suku/', visitorList, name="visitorList"),
	path('Add-Bainaka-Suku/', addVisitor, name="addVisitor"),
	path('Update-Bainaka-Suku/<str:hashid>', updateVisitor, name="updateVisitor"),
	path('Delete-Bainaka-Suku/<str:hashid>', deleteVisitor, name="deleteVisitor"),

	# attendance
	path('Lista-Prezensa/', decisionList, name="decisionList"),
	path('Add-Lista-Prezensa-Enkontru/<str:hashid>', addAttendance, name="addAttendance"),
	path('View-Lista-Prezensa-Enkontru/<str:hashid>', viewAttendance, name="viewAttendance"),
	path('Update-Lista-Prezensa/<str:hashidAttendance>/<str:hashidDecision>', updateAttendance, name="updateAttendance"),
	path('Delete-Lista-Prezensa/<str:hashidAttendance>/<str:hashidDecision>', deletePresence, name="deletePresence"),


	path('LetterIn-Chart/', letterin_charts, name="letterin_charts"),
	path('LetterInByYear-Chart/', letterinbyyear_charts, name="letterinbyyear_charts"),

	path('LetterOut-Chart/', letterout_charts, name="letterout_charts"),
	path('LetterOutByYear-Chart/', letteroutbyyear_charts, name="letteroutbyyear_charts"),
	path('Complaint-Chart/', complaint_charts, name="complaint_charts"),
	path('ComplaintByYear-Chart/', complaintbyyear_charts, name="complaintbyyear_charts"),
	path('visitor-Chart/', visitor_charts, name="visitor_charts"),
	path('visitorByYear-Chart/', visitorbyyear_charts, name="visitorbyyear_charts"),
	path('inventory-Chart/', inventory_charts, name="inventory_charts"),
	path('inventoryAll-Chart/', inventoryall_charts, name="inventoryall_charts"),
	path('decision-Chart/', decision_charts, name="decision_charts"),
	path('decisionAll-Chart/', decisionall_charts, name="decisionall_charts"),
	# path('complaint-Chart/', complaint_charts, name="complaint_charts"),

	# excel export
	path('all-Inventory-Suku/', allInventoryDataToExcel, name="allInventoryDataToExcel"),
	

]