from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Button, HTML
from django.forms.widgets import FileInput
from django.db.models import Q
from .models import *
from employee.models import *
from custom.models import *

class DateInput(forms.DateInput):
	input_type = 'date'
class TimeInput(forms.TimeInput):
	input_type = 'time'

class PositionForm(forms.ModelForm):
	class Meta:
		model = Position
		fields = '__all__'
		exclude=['hashed']
		labels={'name':'Kargu'}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Row(
				Column('name', css_class='form-group col-md-6 mb-0'),
			),
			HTML(""" <div class="text-left mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" title="Update"><span class="btn-label"><i class='fa fa-save'></i></span> Rai</button>"""),
			HTML("""  <button class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</button></div>""")
		)

class PeriodForm(forms.ModelForm):
	class Meta:
		model = MandatePeriod
		fields = '__all__'
		exclude = ['date_created','user_created','hashed']
		labels ={
			'start':"Tinan Mandatu Hahu",
			'end':"Tinan Mandatu Termina",
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Row(
				Column('start', css_class='form-group col-md-6 mb-0'),
				Column('end', css_class='form-group col-md-6 mb-0'),
			),Row(
				Column('status', css_class='form-group col-md-6 mb-0'),
			),
			HTML(""" <div class="text-left mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" title="Update"><span class="btn-label"><i class='fa fa-save'></i></span> Rai</button>"""),
			HTML("""  <button class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</button></div>""")
		)

class LetterInForm(forms.ModelForm):
	letter_date = forms.DateField(label='Data', widget=DateInput())
	subject = forms.CharField(label='Asuntu',widget=forms.Textarea(attrs={'rows':3}))
	class Meta:
		model = LetterIn
		fields = ['letter_date','letter_number','origin','subject','year','attached_file']
		labels={
			'year':'Tinan',
			'origin':'Mai husi',
			'subject':'Asuntu'
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Row(
				Column('letter_date', css_class='form-group col-md-6 mb-0'),
				Column('letter_number', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('origin', css_class='form-group col-md-6 mb-0'),
				Column('subject', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('year', css_class='form-group col-md-6 mb-0'),
				Column('attached_file', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			HTML(""" <div class="text-right mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" title="Update"><span class="btn-label"><i class='fa fa-save'></i></span> Rai</button>"""),
			HTML("""  <button class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</button></div>""")
		)	

class LetterOutForm(forms.ModelForm):
	letter_date = forms.DateField(label='Data Karta', widget=DateInput())
	subject = forms.CharField(label='Asuntu',widget=forms.Textarea(attrs={'rows':3}))
	class Meta:
		model = LetterOut
		fields = ['letter_date','letter_number','destination','subject','year','attached_file']
		labels = {
			'year':"Tinan",
			'village':"Suku",
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Row(
				Column('letter_date', css_class='form-group col-md-6 mb-0'),
				Column('letter_number', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('destination', css_class='form-group col-md-6 mb-0'),
				Column('subject', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('year', css_class='form-group col-md-6 mb-0'),
				Column('attached_file', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			HTML(""" <div class="text-right mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" title="Update"><span class="btn-label"><i class='fa fa-save'></i></span> Rai</button>"""),
			HTML("""  <button class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</button></div>""")
		)

class ExpeditionForm(forms.ModelForm):
	sent_date = forms.DateField(label='Data Haruka Karta', widget=DateInput())
	recieve_date = forms.DateField(label='Data Simu', widget=DateInput(),required=False)
	class Meta:
		model = LetterOutExpedition
		fields = ['year','sent_to','sent_date','recieve_name','recieve_date']
		labels = {
			'sent_date':"Data Haruka",
			'sent_to':"Haruka ba Se",
			'recieve_date':"Data Simu",
			'recieve_name':"Naran ema ne'ebe Simu",
			'year':"Tinan",
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Row(
				Column('sent_date', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('sent_to', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('recieve_date', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('recieve_name', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('year', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			HTML(""" <div class="text-right mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" title="Save"><span class="btn-label"><i class='fa fa-save'></i></span> Rai</button>"""),
			HTML("""  <button class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</button></div>""")
		)

class AttachedExpeditionForm(forms.ModelForm):
	attached_file = forms.FileField(widget=FileInput,label='Aneksu File')
	class Meta:
		model = AttachedExpedition
		fields = ['attached_file']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Row(
				Column('attached_file', css_class='form-group col-xl-6 mb-0'),
				css_class='form-row'
			),
			HTML(""" <div class="text-right mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" title="Save"><span class="btn-label"><i class='fa fa-save'></i></span> Rai</button>"""),
			HTML("""  <button class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</button></div>""")
		)

class ComplaintForm(forms.ModelForm):
	date = forms.DateField(label='Data Keixa', widget=DateInput())
	recieve_date = forms.DateField(label='Data Simu', widget=DateInput())
	class Meta:
		model = Complaint
		fields = ['deficient','year','date','letter_number','identity_number','owner','sex','subject','address',\
				'contact_number','recieve_complait_name','recieve_date','observation','nu_e','nu_p']
		labels = {
			'address':"Hela Fatin",
			'village':"Suku",
			'sex':"Seksu",
			'year':"Tinan",
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['observation'].widget.attrs['rows'] = 2
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Row(
				Column('date', css_class='form-group col-md-6 mb-0'),
				Column('letter_number', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('identity_number', css_class='form-group col-md-4 mb-0'),
				Column('nu_e', css_class='form-group col-md-4 mb-0'),
				Column('nu_p', css_class='form-group col-md-4 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('owner', css_class='form-group col-md-4 mb-0'),
				Column('sex', css_class='form-group col-md-4 mb-0'),
				Column('subject', css_class='form-group col-md-4 mb-0'),
			),
			Row(
				Column('address', css_class='form-group col-md-4 mb-0'),
				Column('contact_number', css_class='form-group col-md-4 mb-0'),
				Column('deficient', css_class='form-group col-md-4 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('recieve_complait_name', css_class='form-group col-md-6 mb-0'),
				Column('recieve_date', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('observation', css_class='form-group col-md-12 mb-0'),
			),
			Row(
				Column('year', css_class='form-group col-md-6 mb-0'),
				# Column('village', css_class='form-group col-md-6 mb-0'),
			),
			HTML(""" <div class="text-right mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" title="Update"><span class="btn-label"><i class='fa fa-save'></i></span> Rai</button>"""),
			HTML("""  <button class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</button></div>""")
		)

class InventoryForm(forms.ModelForm):
	recieve_date = forms.DateField(label='Data Sosa/Simu', widget=DateInput())
	class Meta:
		model = Inventory
		fields = '__all__'
		exclude = ['hashed','user_created','date_created','administrativepost','municipality','village']
		labels = {
			'year':"Tinan",
			'condition':"Kondisaun",
			'category':"Kategoria"
		}
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['category'].widget.attrs.update({'id':'select2-1'})
		self.fields['quantity'].widget.attrs.update({'min':0,'value':1,'oninput':"validity.valid||(value='');"})
		self.fields['unitprice'].widget.attrs.update({'min':0,'value':0,'oninput':"validity.valid||(value='');"})
		# autoselected for year field
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Row(
				Column('name', css_class='form-group col-md-4 mb-0'),
				Column('category', css_class='form-group col-md-4 mb-0'),
				Column('condition', css_class='form-group col-md-4 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('recieve_date', css_class='form-group col-md-4 mb-0'),
				Column('nu_serie', css_class='form-group col-md-4 mb-0'),
				Column('brand', css_class='form-group col-md-4 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('quantity', css_class='form-group col-md-4 mb-0'),
				Column('unitprice', css_class='form-group col-md-4 mb-0'),
				Column('supplier', css_class='form-group col-md-4 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('year', css_class='form-group col-md-4 mb-0'),
			),
			HTML(""" <div class="text-right mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" title="Update"><span class="btn-label"><i class='fa fa-save'></i></span> Rai</button>"""),
			HTML("""  <button class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</button></div>""")
		)

class UsedInventoryDetailForm(forms.ModelForm):
	class Meta:
		model = UsedInventoryDetail
		fields = ['quantity']
		labels = {
			'quantity':"Kuantidade"
		}
		exclude = ['suco','inventory','used','hashed','user_created']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Row(
				Column('quantity', css_class='form-group col-md-6 mb-0'),
			),
			HTML(""" <div class="text-left mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" title="Update"><span class="btn-label"><i class='fa fa-save'></i></span> Rai</button>"""),
			HTML("""  <button class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</button></div>""")
		)

class UsedInventoryForm(forms.ModelForm):
	used_date = forms.DateField(label='Use Date', widget=DateInput())
	class Meta:
		model = UsedInventory
		fields = '__all__'
		exclude = ['hashed','user_created','date_created']
		labels = {
			'inventory':"Naran Inventaria",
			'used_date':"Data Uza",
			'responsavel':"Se mak uza",
			'place':"Uza iha ne'ebe",
		}
	def __init__(self, *args, **kwargs):
		super(UsedInventoryForm, self).__init__(*args, **kwargs)
		self.fields['inventory'].queryset = Inventory.objects.filter(quantity__gt=0)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Row(
				Column('inventory', css_class='form-group col-md-6 mb-0'),
				Column('used_date', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('responsavel', css_class='form-group col-md-6 mb-0'),
				Column('place', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
		)

class CommunityLeadershipForm(forms.ModelForm):
	startMandate = forms.DateField(label='Mandatu Hahu', widget=DateInput())
	endMandate = forms.DateField(label='Mandatu Termina', widget=DateInput())
	class Meta:
		model = CommunityLeadership
		fields = ['population','position','observation','year','period','endMandate','startMandate']
		exclude = ['hashed','user_created','status','aldeia','municipality','administrativepost','village']
		labels = {
			'position':"Pozisaun",
			'period':"Periodu",
			'observation':"Observasaun",
			'year':"Tinan",
		}

	def __init__(self, *args, **kwargs):
		user = kwargs.pop('user',None)
		super().__init__(*args, **kwargs)
		leaderAtivu = CommunityLeadership.objects.filter(status="Yes").values_list('population__id',flat=True)
		self.fields['population'].queryset = Population.objects.exclude(id__in=leaderAtivu).filter(village=user.employee.village.id,status_datap='ac',type_data='f')
		self.fields['period'].queryset = MandatePeriod.objects.filter(status="Ativu")
		leaderAldeia = Position.objects.filter(name__in=("Xefe Aldeia","Delegadu","Delegada"))
		self.fields['position'].queryset = Position.objects.exclude(id__in=leaderAldeia)
		self.fields['observation'].widget.attrs['rows'] = 2
		self.fields['population'].widget.attrs.update({'id':'select2-1'})
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Row(
				Column('population', css_class='form-group col-md-3 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('position', css_class='form-group col-md-4 mb-0'),
				Column('period', css_class='form-group col-md-4 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('startMandate', css_class='form-group col-md-4 mb-0'),
				Column('endMandate', css_class='form-group col-md-4 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('observation', css_class='form-group col-md-6 mb-0'),
				Column('year', css_class='form-group col-md-6 mb-0'),
			),
			HTML(""" <div class="text-right mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" title="Update"><span class="btn-label"><i class='fa fa-save'></i></span> Rai</button>"""),
			HTML("""  <a class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</a></div>""")
		)

class CommunityLeadershipForm1(forms.ModelForm):
	startMandate = forms.DateField(label='Mandatu Hahu', widget=DateInput())
	endMandate = forms.DateField(label='Mandatu Termina', widget=DateInput())
	aldeia = forms.ModelChoiceField(label='Aldeia', queryset = Aldeia.objects.none())
	class Meta:
		model = CommunityLeadership
		fields = ['population','position','observation','year','period','endMandate','startMandate','aldeia']
		exclude = ['hashed','user_created','status','municipality','administrativepost','village']
		labels = {
			'position':"Pozisaun",
			'period':"Periodu",
			'observation':"Observasaun",
			'year':"Tinan",
		}

	def __init__(self, *args, **kwargs):
		userVillage = kwargs.pop('user',None)
		super().__init__(*args, **kwargs)
		self.fields['population'].queryset = Population.objects.none()
		# self.fields['aldeia'].widget.attrs.update({'id':'select2-1'})
		if 'aldeia' in self.data:
			try:
				aldeia = int(self.data.get('aldeia'))
				self.fields['population'].queryset = Population.objects.filter(aldeia__id=aldeia).order_by('name')
			except (ValueError, TypeError):
				pass
		elif self.instance.pk:
			self.fields['population'].queryset = self.instance.aldeia.population_set.order_by('name')
		self.fields['position'].queryset = Position.objects.filter(name__in=("Xefe Aldeia","Delegadu","Delegada"))
		self.fields['period'].queryset = MandatePeriod.objects.filter(status="Ativu")
		self.fields['observation'].widget.attrs['rows'] = 2
		self.fields['aldeia'].queryset = Aldeia.objects.filter(village=userVillage.employee.village.id)
		self.fields['population'].widget.attrs.update({'id':'select2-2'})
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Row(
				Column('aldeia', css_class='form-group col-md-3 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('population', css_class='form-group col-md-4 mb-0'),
				Column('position', css_class='form-group col-md-4 mb-0'),
				Column('period', css_class='form-group col-md-4 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('startMandate', css_class='form-group col-md-4 mb-0'),
				Column('endMandate', css_class='form-group col-md-4 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('observation', css_class='form-group col-md-6 mb-0'),
				Column('year', css_class='form-group col-md-6 mb-0'),
			),
			HTML(""" <div class="text-right mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" title="Update"><span class="btn-label"><i class='fa fa-save'></i></span> Rai</button>"""),
			HTML("""  <a class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</a></div>""")
		)

class ChangeCommunityLeadershipForm(forms.ModelForm):
	startMandate = forms.DateField(label='Mandatu Hahu', widget=DateInput())
	endMandate = forms.DateField(label='Mandatu Termina', widget=DateInput())
	class Meta:
		model = CommunityLeadership
		fields = ['population','observation','year','endMandate','startMandate']
		exclude = ['hashed','user_created','status','period','position']
		labels = {
			'population':"Naran Kompletu",
			'observation':"Observasaun",
			'year':"Tinan",
		}

	def __init__(self, *args, village=None, **kwargs):
		super(ChangeCommunityLeadershipForm,self).__init__(*args, **kwargs)
		inner_qs = CommunityLeadership.objects.filter(village=village,position__name="Xefe Suku",status="Yes").values_list('population__id',flat=True) 
		self.fields['population'].queryset = Population.objects.exclude(id__in=inner_qs).filter(village=village,status_datap='ac',type_data='f')
		self.fields['population'].widget.attrs.update({'id':'select2-1'})
		self.fields['observation'].widget.attrs['rows'] = 2
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Row(
				Column('population', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('startMandate', css_class='form-group col-md-3 mb-0'),
				Column('endMandate', css_class='form-group col-md-3 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('observation', css_class='form-group col-md-6 mb-0'),
			),
			Row(
				Column('year', css_class='form-group col-md-6 mb-0'),
			),
			HTML(""" <div class="text-left mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" title="Save"><span class="btn-label"><i class='fa fa-save'></i></span> Rai</button>"""),
			HTML("""  <a class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</a></div>""")
		)

class CommunityLeadershipUpdateForm(forms.ModelForm):
	startMandate = forms.DateField(label='Mandatu Hahu', widget=DateInput())
	endMandate = forms.DateField(label='Mandatu Termina', widget=DateInput())
	class Meta:
		model = CommunityLeadership
		fields = ['population','position','observation','year','period','endMandate','startMandate']
		exclude = ['hashed','user_created']
		labels = {
			'population':"Naran Kompletu",
			'position':"Pozisaun",
			'period':"Periodu",
			'observation':"Observasaun",
			'year':"Tinan",
		}

	def __init__(self, *args, **kwargs):
		user = kwargs.pop('user',None)
		data = kwargs.pop('data',None)
		super().__init__(*args, **kwargs)
		self.fields['population'].queryset = Population.objects.filter(village=user.employee.village.id,status_datap='ac',type_data='f')
		self.fields['population'].widget.attrs.update({'id':'select2-1'})
		if data.position.name != "Xefe Suku":
			inner_qs = CommunityLeadership.objects.filter(village=user.employee.village.id,position__name="Xefe Suku",status="Yes").values_list('position__id',flat=True)
			self.fields['position'].queryset = Position.objects.exclude(id__in=inner_qs)
		self.fields['observation'].widget.attrs['rows'] = 2
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Row(
				Column('population', css_class='form-group col-md-4 mb-0'),
				Column('position', css_class='form-group col-md-4 mb-0'),
				Column('period', css_class='form-group col-md-4 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('startMandate', css_class='form-group col-md-4 mb-0'),
				Column('endMandate', css_class='form-group col-md-4 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('observation', css_class='form-group col-md-6 mb-0'),
				Column('year', css_class='form-group col-md-6 mb-0'),
			),
			HTML(""" <div class="text-right mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" title="Update"><span class="btn-label"><i class='fa fa-save'></i></span> Rai</button>"""),
			HTML("""  <button class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</button></div>""")
		)

class VisitorForm(forms.ModelForm):
	visitDate = forms.DateField(label='Data Vizita', widget=DateInput())
	entryTime = forms.TimeField(label='Oras Tama', widget=TimeInput())
	outTime = forms.TimeField(label='Oras Sai', widget=TimeInput())
	class Meta:
		model = Visitor
		fields = '__all__'
		exclude = ['hashed','user_created','signature','administrativepost','village','municipality']
		labels = {
			'sex':"Seksu",
			'deficient':"Kondisaun Fíziku",
			'year':"Tinan",
			'name':"Naran Bainaka",
			'visitor':"Instituisaun/Ministeriu/Organizasaun",
			'subject':"Asuntu",
			'address':"Enderesu",
			'contact_number':"Nú. Telefone",
			'observation':"Observasaun",
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['observation'].widget.attrs['rows'] = 2
		self.fields['subject'].widget.attrs['rows'] = 2
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Row(
				Column('visitDate', css_class='form-group col-md-4 mb-0'),
				Column('entryTime', css_class='form-group col-md-4 mb-0'),
				Column('outTime', css_class='form-group col-md-4 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('name', css_class='form-group col-md-4 mb-0'),
				Column('sex', css_class='form-group col-md-4 mb-0'),
				Column('deficient', css_class='form-group col-md-4 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('visitor', css_class='form-group col-md-6 mb-0'),
				Column('subject', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('address', css_class='form-group col-md-6 mb-0'),
				Column('contact_number', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('observation', css_class='form-group col-md-6 mb-0'),
				Column('year', css_class='form-group col-md-6 mb-0'),
			),
			HTML(""" <div class="text-right mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" title="Update"><span class="btn-label"><i class='fa fa-save'></i></span> Rai</button>"""),
			HTML("""  <button class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</button></div>""")
		)

class AttendanceForm(forms.ModelForm):
	# xefe_suku = CommunityLeadership.objects.filter(position__name="Xefe Suku").values_list('population__id',flat=True) 
	# name = forms.ModelChoiceField(label='Naran Kompletu', queryset = Population.objects.exclude(id__in=xefe_suku).filter(status_datap='ac',type_data='f')) 
	class Meta:
		model = Attendance
		fields = ['instituition','position','name','sex','deficient']
		exclude = ['signature','administrativepost','village','municipality','decision','date_created','hashed','year','user_created']
		labels = {
			'name':"Naran Kompletu",
			'instituition':"Diresaun/Instituisaun",
			'position':"Pozisaun",
			'deficient':"Kondisaun Fíziku",
			'sex':"Seksu",
		}
	def __init__(self, *args, **kwargs):
		super(AttendanceForm, self).__init__(*args, **kwargs)
		self.fields['name'].required = True
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Row(
				Column('name', css_class='form-group col-md-6 mb-0'),
				Column('sex', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('instituition', css_class='form-group col-md-6 mb-0'),
				Column('position', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			Row(
				Column('deficient', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			HTML(""" <div class="text-rigth mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" name="save" title="Save"><span class="btn-label"><i class='fa fa-save'></i></span> Rai</button>"""),
			HTML(""" {% if page != "update" %}<button class="btn btn-sm btn-labeled btn-primary" type="submit" name="save_and_add_another" title="Save and Continue Adding"><span class="btn-label"><i class='fa fa-save'></i></span> Rai no Adisiona Lista</button>{% endif %}"""),
			HTML("""  <button class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</button></div>""")
		)

class MeetingForm(forms.ModelForm):
	initial_time = forms.TimeField(label="Komesa (Oras)",widget=TimeInput())
	end_time = forms.TimeField(label="Remata (Oras)",widget=TimeInput())
	prepared_date = forms.DateField(label='Data', widget=DateInput())
	aproved_date = forms.DateField(label='Data', widget=DateInput())
	class Meta:
		model = MeetingTime
		fields = ['initial_time','end_time','facilitator','community_representative','attach_attendence_list',\
				'discussion','decision_takes','diversus','prepared_by','prepared_date','aproved_date']
		exclude = ['year','lideransa_komunitaria','user_created','decision','village','municipality','administrativepost','meeting_agenda','date_created','hashed']
		labels = {
			'prepared_by':"Naran Kompletu",
			'facilitator':"Enkontru Fasilita husi",
			'community_representative':"Ema seluk ne'ebe reprezenta komunidade",
			'attach_attendence_list':"Lista prezensa iha aneksu",
			'discussion':"Rezumu diskusaun tuir Ajenda Enkontru",
			'decision_takes':"Desizaun ne'ebe foti",
			'diversus':"Diversus",
			'diversus':"Diversus",
		}
	def __init__(self, *args, **kwargs):
		super(MeetingForm, self).__init__(*args, **kwargs)
		self.fields['initial_time'].required = True
		self.fields['discussion'].widget.attrs['rows'] = 2
		self.fields['decision_takes'].widget.attrs['rows'] = 2
		self.fields['diversus'].widget.attrs['rows'] = 2
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Row(
				Column(HTML("""
						<div class="col-md-12">
                          <div class="form-group mb-3"><label>Tinan</label>
                            <select class="form-control" name="year" id="select2-1">
                              {% for i in year %}
                              {% if i.year == currentYear %}
                              	<option value="{{i.year}}" selected>{{i.year}}</option>
                              {% else %}
                              	<option value="{{i.year}}">{{i.year}}</option>
                              {% endif %}
                              {% endfor %}
                            </select>
                          </div>
                        </div>
						""")
				),
				Column(HTML("""
						<div class="col-md-12">
                          <div class="form-group mb-3"><label>Data Enkontru</label>
                            <input class="form-control" type="date" value="{{decision.meeting_date|date:'Y-m-d'}}" name="meeting_date" readonly>
                          </div>
                        </div>
						"""),
				),
				Column('initial_time', css_class='form-group col-md-3 mb-0'),
				Column('end_time', css_class='form-group col-md-3 mb-0'),
				css_class='form-row'
			),
			Row(
				Column(
				Column('facilitator', css_class='form-group col-md-12 mb-0'),
				Column('community_representative', css_class='form-group col-md-12 mb-0'),
				Column('attach_attendence_list', css_class='form-group col-md-12 mb-0'),
				),
				Column(HTML("""
				<div class="col-md-12">
                          <div class="form-group mb-3">
                            <p class="bg-info text-center p-2 mb-3"><b>Membru reprezentante husi Konsellu Suku ne'ebe mak auzente (la marka prezensa) iha enkontru</b></p>
                            <table class="table table-bordered table-sm table-hover">
                                <tr>
                                  <th class="text-center">Nú.</th>
                                  <th class="text-center">Naran Kompletu</th>
                                  <th class="text-center">Pozisaun</th>
                                </tr>
                            {% for i in villageAdviseAbsentInDecision %}
                              <tr>
                                <td class="text-center">{{forloop.counter}}</td>
                                <td>{{i.villageAdvise.population.name}}</td>
                                <td>{{i.villageAdvise.position}}</td>
                              </tr>
                            {% endfor %}
                            </table>
                          </div>
                        </div>	
				"""),),
				css_class='form-row'
			),
			HTML("""
					<div class="col-sm-12 row">
	                  <label class="col-md-2">Ajenda Enkontru</label>
	                  <div class="form-group col-md-10 mb-3">
	                    <div class="input-group mb-1">
	                      <div name="decision_takes" readonly class="col-md-12 border p-3" style="background-color: #edf1f2">{% for i in getVotingResult %}{{forloop.counter}}. {{i.decision_on}}<br>{% endfor %}</div>
	                    </div>
	                  </div>
	                </div>
				"""),
			Row(
				Column('discussion', css_class='form-group col-md-12 mb-0'),
			),
			Row(
				Column('decision_takes', css_class='form-group col-md-12 mb-0'),
			),
			Row(
				Column('diversus', css_class='form-group col-md-12 mb-0'),
			),
			Row(Column(HTML("""
						<label class="col-md-12">Minutas Enkontru prepara husi :</label>
						"""),
				),
				Column('prepared_by', css_class='form-group col-md-5 mb-0'),
				Column('prepared_date', css_class='form-group col-md-5 mb-0'),
				css_class='form-row'
			),
			Row(
				Column(HTML("""
						<label class="col-md-8">Minutas Aprova husi Xefe Suku :</label>
						"""),
				),Column(HTML("""
                            <div class="col-md-12 mb-3"><label>Naran Kompletu</label>
                              <input class="form-control" type="text" value="{{xefe_suku.population.name}}" readonly>
                            </div>
						"""),
				),
				Column('aproved_date', css_class='form-group col-md-5 mb-0'),
				css_class='form-row'
			),
			HTML(""" <div class="text-right mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" name="save" title="Save"><span class="btn-label"><i class='fa fa-save'></i></span> Rai</button>"""),
			HTML("""  <button class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</button></div>""")
		)

class DecisionResultForm(forms.ModelForm):
	class Meta:
		model = VotingResult
		fields = '__all__'
		exclude = ['hashed','user_created','user_created','decision','municipality','administrativepost','village']
		labels = {
			'decision_on':"Desizaun Kona-ba",
			'vote_afavor':"Vota Afavor",
			'vote_kontra':"Vota Kontra",
			'vote_abstein':"Vota Abstein",
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['vote_afavor'].widget.attrs.update({'min':0,'value':0,'oninput':"validity.valid||(value='');"})
		self.fields['vote_kontra'].widget.attrs.update({'min':0,'value':0,'oninput':"validity.valid||(value='');"})
		self.fields['vote_abstein'].widget.attrs.update({'min':0,'value':0,'oninput':"validity.valid||(value='');"})
		self.fields['decision_on'].widget.attrs['rows'] = 2
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Row(
				Column('decision_on', css_class='form-group col-md-6 mb-0'),
				css_class='form-row'
			),
			HTML("""<div class="col-sm-12 mt-3">
                          <p class="bg-info text-center p-2 mb-3"><b>Rezultadu ho Votasaun</b></p>
                        </div>"""),
			Row(
				Column('vote_afavor', css_class='form-group col-md-4 mb-0'),
				Column('vote_kontra', css_class='form-group col-md-4 mb-0'),
				Column('vote_abstein', css_class='form-group col-md-4 mb-0'),
				css_class='form-row'
			),
			HTML(""" <div class="text-right mt-4"> <button class="btn btn-sm btn-labeled btn-info" type="submit" title="Save"><span class="btn-label"><i class='fa fa-save'></i></span> Rai</button>"""),
			HTML("""  <button class="btn btn-sm btn-labeled btn-secondary" onclick=self.history.back()><span class="btn-label"><i class="fa fa-window-close"></i></span> Kansela</button></div>""")
		)

