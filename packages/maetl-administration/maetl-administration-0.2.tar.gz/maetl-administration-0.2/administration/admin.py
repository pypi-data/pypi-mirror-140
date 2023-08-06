from django.contrib import admin
from administration.models import *
# Register your models here.

from import_export import resources

from import_export.admin import ImportExportModelAdmin


class PositionResource(resources.ModelResource):
    class Meta:
        model = Position
class PositionAdmin(ImportExportModelAdmin):
    resource_class = PositionResource
admin.site.register(Position,PositionAdmin)


class DecisionResource(resources.ModelResource):
    class Meta:
        model = Decision
class DecisionAdmin(ImportExportModelAdmin):
    resource_class = DecisionResource
admin.site.register(Decision,DecisionAdmin)



class VotingResultResource(resources.ModelResource):
    class Meta:
        model = VotingResult
class VotingResultAdmin(ImportExportModelAdmin):
    resource_class = VotingResultResource
admin.site.register(VotingResult,VotingResultAdmin)



class DecisionDetailResource(resources.ModelResource):
    class Meta:
        model = DecisionDetail
class DecisionDetailAdmin(ImportExportModelAdmin):
    resource_class = DecisionDetailResource
admin.site.register(DecisionDetail,DecisionDetailAdmin)



class InventoryResource(resources.ModelResource):
    class Meta:
        model = Inventory
class InventoryAdmin(ImportExportModelAdmin):
    resource_class = InventoryResource
admin.site.register(Inventory,InventoryAdmin)



class UsedInventoryResource(resources.ModelResource):
    class Meta:
        model = UsedInventory
class UsedInventoryAdmin(ImportExportModelAdmin):
    resource_class = UsedInventoryResource
admin.site.register(UsedInventory,UsedInventoryAdmin)


class UsedInventoryDetailResource(resources.ModelResource):
    class Meta:
        model = UsedInventoryDetail
class UsedInventoryDetailAdmin(ImportExportModelAdmin):
    resource_class = UsedInventoryDetailResource
admin.site.register(UsedInventoryDetail,UsedInventoryDetailAdmin)





class LetterInResource(resources.ModelResource):
    class Meta:
        model = LetterIn
class LetterInAdmin(ImportExportModelAdmin):
    resource_class = LetterInResource
admin.site.register(LetterIn,LetterInAdmin)



class LetterOutResource(resources.ModelResource):
    class Meta:
        model = LetterOut
class LetterOutAdmin(ImportExportModelAdmin):
    resource_class = LetterOutResource
admin.site.register(LetterOut,LetterOutAdmin)


class LetterOutExpeditionResource(resources.ModelResource):
    class Meta:
        model = LetterOutExpedition
class LetterOutExpeditionAdmin(ImportExportModelAdmin):
    resource_class = LetterOutExpeditionResource
admin.site.register(LetterOutExpedition,LetterOutExpeditionAdmin)


class AttachedExpeditionResource(resources.ModelResource):
    class Meta:
        model = AttachedExpedition
class AttachedExpeditionAdmin(ImportExportModelAdmin):
    resource_class = AttachedExpeditionResource
admin.site.register(AttachedExpedition,AttachedExpeditionAdmin)



class CommunityLeadershipResource(resources.ModelResource):
    class Meta:
        model = CommunityLeadership
class CommunityLeadershipAdmin(ImportExportModelAdmin):
    resource_class = CommunityLeadershipResource
admin.site.register(CommunityLeadership,CommunityLeadershipAdmin)



class ComplaintResource(resources.ModelResource):
    class Meta:
        model = Complaint
class ComplaintAdmin(ImportExportModelAdmin):
    resource_class = ComplaintResource
admin.site.register(Complaint,ComplaintAdmin)



class MeetingTimeResource(resources.ModelResource):
    class Meta:
        model = MeetingTime
class MeetingTimeAdmin(ImportExportModelAdmin):
    resource_class = MeetingTimeResource
admin.site.register(MeetingTime,MeetingTimeAdmin)



class VisitorResource(resources.ModelResource):
    class Meta:
        model = Visitor
class VisitorAdmin(ImportExportModelAdmin):
    resource_class = VisitorResource
admin.site.register(Visitor,VisitorAdmin)

class MandatePeriodResource(resources.ModelResource):
    class Meta:
        model = MandatePeriod
class MandatePeriodAdmin(ImportExportModelAdmin):
    resource_class = MandatePeriodResource
admin.site.register(MandatePeriod,MandatePeriodAdmin)



class AttendanceResource(resources.ModelResource):
    class Meta:
        model = Attendance
class AttendanceAdmin(ImportExportModelAdmin):
    resource_class = AttendanceResource
admin.site.register(Attendance,AttendanceAdmin)