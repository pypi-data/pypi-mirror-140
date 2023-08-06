from django.db import models
from django.contrib.auth.models import User
from population.models import *
from custom.models import *

# Create your models here.
DECISION_TYPE = (
		("Konsellu Suku", "Konsellu Suku"),
		("Xefe Suku", "Xefe Suku"),
	)
ACTIVE = (
		("Yes", "Yes"),
		("No", "No"),
	)
STATUSPERIOD = (
		("Ativu", "Ativu"),
		("Desativu", "Desativu"),
	)

CONDITION = (
		("Diak", "Diak"),
		("Aat", "Aat"),
	)

class Position(models.Model):
	name = models.CharField(max_length=100)

	def __str__(self):
		template = '{0.name}'
		return template.format(self)

	class Meta:
		verbose_name_plural = 'A7. Kargu'

class MandatePeriod(models.Model):
	user_created =  models.ForeignKey(User, on_delete=models.CASCADE)
	start = models.CharField(max_length=4,null=True)
	end = models.CharField(max_length=4,null=True)
	status = models.CharField(max_length=8,choices=STATUSPERIOD,null=True)
	date_created = models.DateTimeField(auto_now_add=True)
	hashed = models.CharField(max_length=32, null=True, blank=True)
	def __str__(self):
		template = "{0.start} to'o {0.end}"
		return template.format(self)
	class Meta:
		verbose_name_plural = 'A7. Periodu Mandatu'

# ================================
class Decision(models.Model):
	year = models.ForeignKey(Year, on_delete=models.CASCADE,null=True)
	village = models.ForeignKey(Village, on_delete=models.CASCADE,null=True)
	administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE,null=True)
	municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE,null=True)
	user_created =  models.ForeignKey(User, on_delete=models.CASCADE)
	decision_type = models.CharField(max_length=20, choices=DECISION_TYPE)
	meeting_date = models.DateField(auto_now_add=False)
	decision_number = models.CharField(max_length=100)
	date_created = models.DateTimeField(auto_now_add=True)
	hashed = models.CharField(max_length=32, null=True, blank=True)
	observation = models.TextField(null=True,blank=True)

	def __str__(self):
		template = '{0.decision_number}'
		return template.format(self)

	def getAfavor(self):
		return VotingResult.objects.only('vote_afavor').get(decision=self).vote_afavor

	def getKontra(self):
		return VotingResult.objects.only('vote_kontra').get(decision=self).vote_kontra

	def getAbstein(self):
		return VotingResult.objects.only('vote_abstein').get(decision=self).vote_abstein
	def getVotingResult(self):
		return VotingResult.objects.filter(decision=self)

	def getCountVillageAdvise(self):
		return DecisionDetail.objects.filter(decision=self).count()
	def getVillageAdviseAll(self):
		return DecisionDetail.objects.filter(decision=self)
	def getVillageAdviseFirst(self):
		return DecisionDetail.objects.filter(decision=self)[0]
	def getVillageAdviseSecondAll(self):
		return DecisionDetail.objects.filter(decision=self)[1:]

	class Meta:
		verbose_name_plural = 'A1 & A2. Livru Desizaun Suku'

class VotingResult(models.Model):
	village = models.ForeignKey(Village, on_delete=models.CASCADE,null=True)
	administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE,null=True)
	municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE,null=True)
	decision = models.ForeignKey(Decision, on_delete=models.CASCADE)
	decision_on = models.TextField(null=True)
	vote_afavor = models.IntegerField()
	vote_kontra = models.IntegerField()
	vote_abstein = models.IntegerField()
	user_created =  models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	date_created = models.DateTimeField(auto_now_add=True,null=True)
	hashed = models.CharField(max_length=32, null=True, blank=True)

	def __str__(self):
		template = '{0.decision_on}'
		return template.format(self)
	class Meta:
		verbose_name_plural = 'A1 & A2. Rezultadu Votasaun Desizaun Suku'

# lideransa komunitaria
class CommunityLeadership(models.Model):
	year = models.ForeignKey(Year, on_delete=models.CASCADE,null=True)
	population = models.ForeignKey(Population, on_delete=models.CASCADE,verbose_name="Naran Lideransa")
	position = models.ForeignKey(Position,on_delete=models.CASCADE)
	village = models.ForeignKey(Village, on_delete=models.CASCADE,null=True)
	administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE,null=True)
	municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE,null=True)
	user_created =  models.ForeignKey(User, on_delete=models.CASCADE)
	period = models.ForeignKey(MandatePeriod,on_delete=models.CASCADE,null=True)
	startMandate = models.DateField(auto_now_add=False,null=True)
	endMandate = models.DateField(auto_now_add=False,null=True)
	status = models.CharField(max_length=4, choices=ACTIVE,null=True)
	observation = models.TextField(null=True,blank=True)
	aldeia = models.CharField(max_length=50,null=True,blank=True)

	date_created = models.DateTimeField(auto_now_add=True)
	hashed = models.CharField(max_length=32, null=True, blank=True)
	def __str__(self):
		template = 'Naran : {0.population.name}, Kargu : {0.position}, Periodu:{0.period}, Suku: {0.village}'
		return template.format(self)
	class Meta:
		verbose_name_plural = 'A7. Livru Lideransa Komunitaria'


class DecisionDetail(models.Model):
	village = models.ForeignKey(Village, on_delete=models.CASCADE,null=True)
	administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE,null=True)
	municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE,null=True)
	decision = models.ForeignKey(Decision, on_delete=models.CASCADE)
	villageAdvise = models.ForeignKey(CommunityLeadership, on_delete=models.CASCADE)
	attendance = models.CharField(max_length=10, choices=ACTIVE,null=True)
	def __str__(self):
		template = '{0.decision}'
		return template.format(self)
	class Meta:
		verbose_name_plural = 'A1 & A2. Detaillu Desizaun Suku'

# model inventoria
class Inventory(models.Model):
	category = models.CharField(choices=[('Mobiliáriu','Mobiliáriu'),('Transporte','Transporte'),('Elektróniku','Elektróniku'),('Rai','Rai'),('Uma','Uma'),('Nesesidade Bázika','Nesesidade Bázika'),('Animál','Animál'),('Plantas','Plantas'),('Seluk','Seluk')], max_length=30, null=True, verbose_name="Kategoria")
	supplier = models.CharField(max_length=100,null=True,verbose_name="Fontes/Se mak fo")
	user_created =  models.ForeignKey(User, on_delete=models.CASCADE)
	village = models.ForeignKey(Village, on_delete=models.CASCADE,null=True)
	administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE,null=True)
	municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE,null=True)
	year = models.ForeignKey(Year, on_delete=models.CASCADE,null=True)
	name = models.CharField(max_length=100,verbose_name="Naran Inventária")
	recieve_date = models.DateField(auto_now_add=False)
	condition = models.CharField(choices=[('Diak','Diak'),('Diak Natoon','Diak Natoon'),('Aat','Aat'),('Aat Total','Aat Total')],max_length=30,null=True)
	nu_serie = models.CharField(max_length=100,verbose_name="Nu Seri")
	quantity = models.IntegerField(verbose_name="Kuantidade")
	unitprice = models.DecimalField(decimal_places=2,max_digits=10,verbose_name="Folin Sosa",null=True)
	brand = models.CharField(max_length=100,verbose_name="Marka")

	date_created = models.DateTimeField(auto_now_add=True)
	hashed = models.CharField(max_length=32, null=True, blank=True)
	def __str__(self):
		template = '{0.name}'
		return template.format(self)
	class Meta:
		verbose_name_plural = 'A3. Livru Inventáriu Suku'

class UsedInventory(models.Model):
	village = models.ForeignKey(Village, on_delete=models.CASCADE,null=True)
	administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE,null=True)
	municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE,null=True)
	user_created =  models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	used_date = models.DateField(auto_now_add=False)
	responsible = models.CharField(choices=[('Xefe Suku','Xefe Suku'),('PAAs','PAAs'),('Xefe Aldeia','Xefe Aldeia'),('Populasaun','Populasaun')],max_length=50,null=True)
	place = models.CharField(max_length=100)

	date_created = models.DateTimeField(auto_now_add=True)
	hashed = models.CharField(max_length=32, null=True, blank=True)
	def __str__(self):
		template = '{0.responsible}'
		return template.format(self)
	class Meta:
		verbose_name_plural = 'A3. Inventáriu Uzadu'

class UsedInventoryDetail(models.Model):
	inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE,null=True)
	used = models.ForeignKey(UsedInventory, on_delete=models.CASCADE,null=True)
	village = models.ForeignKey(Village, on_delete=models.CASCADE,null=True)
	administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE,null=True)
	municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE,null=True)
	user_created =  models.ForeignKey(User, on_delete=models.CASCADE)
	quantity = models.IntegerField()

	date_created = models.DateTimeField(auto_now_add=True)
	hashed = models.CharField(max_length=32, null=True, blank=True)
	def __str__(self):
		template = '{0.inventory}'
		return template.format(self)
	class Meta:
		verbose_name_plural = 'A3. Detallu Inventáriu Uzadu'

# model Karta tama no Karta sai
class LetterIn(models.Model):
	year = models.ForeignKey(Year, on_delete=models.CASCADE,null=True)
	village = models.ForeignKey(Village, on_delete=models.CASCADE, null=True,blank=True)
	administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE, null=True,blank=True)
	municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, null=True,blank=True)
	user_created =  models.ForeignKey(User, on_delete=models.CASCADE)
	letter_date = models.DateField(auto_now_add=False)
	letter_number = models.CharField(max_length=100,verbose_name="Nú. Karta")
	origin = models.CharField(max_length=100,verbose_name="Orijen Karta")
	subject = models.CharField(max_length=200,verbose_name="Asuntu Karta")
	attached_file = models.FileField(upload_to = 'file/letterIn/', blank=True,null=True,verbose_name="Upload File")

	date_created = models.DateTimeField(auto_now_add=True)
	hashed = models.CharField(max_length=32, null=True, blank=True)
	def __str__(self):
		template = '{0.subject}'
		return template.format(self)
	class Meta:
		verbose_name_plural = 'A5. Livru Ajenda Karta Tama'

class LetterOut(models.Model):
	year = models.ForeignKey(Year, on_delete=models.CASCADE,null=True)
	village = models.ForeignKey(Village, on_delete=models.CASCADE,null=True)
	administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE,null=True)
	municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE,null=True)
	user_created =  models.ForeignKey(User, on_delete=models.CASCADE)
	letter_date = models.DateField(auto_now_add=False)
	letter_number = models.CharField(max_length=100,verbose_name="Nú. Karta")
	subject = models.CharField(max_length=200,verbose_name="Asuntu Karta")
	destination = models.CharField(max_length=100,verbose_name="Diriji ba se")
	attached_file = models.FileField(upload_to = 'file/letterOut/', blank=True,null=True,verbose_name="Upload File")
	
	date_created = models.DateTimeField(auto_now_add=True)
	hashed = models.CharField(max_length=32, null=True, blank=True)
	def __str__(self):
		template = 'Asuntu Karta : {0.subject} | {0.destination} | {0.letter_number}'
		return template.format(self)
	def getExpeditionAttachedFile(self):
		return AttachedExpedition.objects.get(letter_out=self)
	class Meta:
		verbose_name_plural = 'A4. Livru Ajenda Karta Sai'

class LetterOutExpedition(models.Model):
	year = models.ForeignKey(Year, on_delete=models.CASCADE,null=True)
	village = models.ForeignKey(Village, on_delete=models.CASCADE,null=True)
	administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE,null=True)
	municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE,null=True)
	user_created =  models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	letter_out = models.ForeignKey(LetterOut,on_delete=models.CASCADE,null=True)
	sent_date = models.DateField(auto_now_add=False,verbose_name="Data Haruka",null=True,blank=True)
	sent_to = models.CharField(max_length=100,null=True,blank=True)
	recieve_name = models.CharField(max_length=100,verbose_name="Simu husi",null=True,blank=True)
	recieve_date = models.DateField(auto_now_add=False,verbose_name="Data Simu",null=True,blank=True)
	signature = models.CharField(max_length=20,null=True,blank=True)
	date_created = models.DateTimeField(auto_now_add=True,null=True)
	hashed = models.CharField(max_length=32, null=True, blank=True)
	def __str__(self):
		template = '{0.recieve_name}'
		return template.format(self)
	class Meta:
		verbose_name_plural = 'A6. Livru Espedisaun'

class AttachedExpedition(models.Model):
	village = models.ForeignKey(Village, on_delete=models.CASCADE,null=True)
	administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE,null=True)
	municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE,null=True)
	letter_out = models.ForeignKey(LetterOut,on_delete=models.CASCADE)
	user_created =  models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	attached_file = models.FileField(upload_to = 'file/expedition/', blank=True,null=True,verbose_name="Upload File")
	date_created = models.DateTimeField(auto_now_add=True,null=True)
	hashed = models.CharField(max_length=32, null=True, blank=True)
	def __str__(self):
		template = '{0.letter_out}'
		return template.format(self)
	class Meta:
		verbose_name_plural = 'A6. Aneksu File Espedisaun'

# rejistu keixa
class Complaint(models.Model):
	year = models.ForeignKey(Year, on_delete=models.CASCADE,null=True)
	village = models.ForeignKey(Village, on_delete=models.CASCADE,null=True)
	administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE,null=True)
	municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE,null=True)
	user_created =  models.ForeignKey(User, on_delete=models.CASCADE)
	date = models.DateField(auto_now_add=False,verbose_name="Data Keixa")
	letter_number = models.CharField(max_length=100,verbose_name="Númeru Karta")
	identity_number =  models.CharField(max_length=100, verbose_name="Nú. Billete Identidade")
	nu_e = models.CharField(max_length=25,verbose_name="Nú. Kartaun Eleitoral",blank=True,null=True)
	nu_p = models.CharField(max_length=50,verbose_name="Nú. Pasaporte",blank=True,null=True)
	owner = models.CharField(max_length=100, verbose_name="Naran Keixa Nain")
	sex = models.CharField(choices=[('Mane','Mane'),('Feto','Feto'),('Seluk','Seluk')],max_length=10,null=True)
	subject = models.CharField(max_length=100, verbose_name="Asuntu Keixa")
	address = models.CharField(max_length=100,verbose_name="Enderesu")
	contact_number = models.CharField(max_length=30,verbose_name="Nú. Kontaktu")
	recieve_complait_name = models.CharField(max_length=100,verbose_name="Naran Simu")
	recieve_date = models.DateField(auto_now_add=False,verbose_name="Data Simu")
	deficient =  models.ForeignKey(Deficient,on_delete=models.CASCADE,verbose_name='Kondisaun Fíziku',null=True,blank=True)
	observation = models.TextField(verbose_name="Observasaun",null=True,blank=True)

	date_created = models.DateTimeField(auto_now_add=True)
	hashed = models.CharField(max_length=32, null=True, blank=True)
	def __str__(self):
		template = '{0.subject}'
		return template.format(self)
	class Meta:
		verbose_name_plural = 'A10. Rejistu Keixa Suku'

		

# minuta enkontru Suku
class MeetingTime(models.Model):
	year = models.ForeignKey(Year, on_delete=models.CASCADE,null=True)
	lideransa_komunitaria = models.ForeignKey(CommunityLeadership, on_delete=models.CASCADE)
	village = models.ForeignKey(Village, on_delete=models.CASCADE,null=True)
	administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE,null=True)
	municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE,null=True)
	user_created =  models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	decision = models.ForeignKey(Decision, on_delete=models.CASCADE,null=True)
	initial_time = models.TimeField(max_length=10)
	end_time = models.TimeField(max_length=10)
	facilitator =  models.CharField(max_length=100)
	community_representative = models.CharField(max_length=100,null=True)
	attach_attendence_list = models.CharField(max_length=4, choices=[('Sim','Sim'),('Lae','Lae')])
	meeting_agenda = models.TextField()
	discussion = models.TextField()
	decision_takes = models.TextField(null=True)
	diversus = models.TextField(null=True)
	prepared_by = models.CharField(max_length=100)
	prepared_date = models.DateField(auto_now_add=False,null=True)
	aproved_date = models.DateField(auto_now_add=False,null=True)
	date_created = models.DateTimeField(auto_now_add=True)
	hashed = models.CharField(max_length=32, null=True, blank=True)
	def __str__(self):
		template = '{0.meeting_agenda}'
		return template.format(self)
	def meeting_agendaList(self):
		return self.meeting_agenda.split(',')
	class Meta:
		verbose_name_plural = 'A9. Minutas Enkontru Suku'


class Visitor(models.Model):
	year = models.ForeignKey(Year, on_delete=models.CASCADE,null=True)
	village = models.ForeignKey(Village, on_delete=models.CASCADE,null=True)
	administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE,null=True)
	municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE,null=True)
	user_created =  models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	visitDate = models.DateField(auto_now_add=False)
	entryTime = models.TimeField()
	outTime = models.TimeField()
	name = models.CharField(max_length=100,null=True)
	sex = models.CharField(choices=[('Mane','Mane'),('Feto','Feto'),('Seluk','Seluk')],max_length=10,null=True)
	deficient =  models.ForeignKey(Deficient,on_delete=models.CASCADE,verbose_name='Kondisaun Fíziku',null=True,blank=True)
	visitor = models.CharField(max_length=100,null=True)
	subject = models.TextField(null=True)
	address = models.CharField(max_length=100,null=True)
	contact_number = models.CharField(max_length=20,null=True)
	signature = models.CharField(max_length=20,null=True, blank=True)
	observation = models.TextField(null=True,blank=True)
	date_created = models.DateTimeField(auto_now_add=True)
	hashed = models.CharField(max_length=32, null=True, blank=True)

	def __str__(self):
		template = '{0.name}'
		return template.format(self)

	class Meta:
		verbose_name_plural = 'A11. Livru Bainaka Suku'

class Attendance(models.Model):
	year = models.ForeignKey(Year, on_delete=models.CASCADE,null=True)
	village = models.ForeignKey(Village, on_delete=models.CASCADE,null=True)
	administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE,null=True)
	municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE,null=True)
	user_created =  models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	decision = models.ForeignKey(Decision, on_delete=models.CASCADE,null=True)
	name = models.CharField(max_length=500,null=True,blank=True)
	sex = models.CharField(choices=[('Mane','Mane'),('Feto','Feto'),('Seluk','Seluk')],max_length=10,null=True)
	instituition = models.CharField(max_length=500,null=True,blank=True)
	position = models.CharField(max_length=500,null=True,blank=True)
	deficient =  models.ForeignKey(Deficient,on_delete=models.CASCADE,verbose_name='Kondisaun Fíziku',null=True)
	signature = models.CharField(max_length=500,null=True,blank=True)
	date_created = models.DateTimeField(auto_now_add=True)
	hashed = models.CharField(max_length=32, null=True, blank=True)

	def __str__(self):
		template = '{0.name}'
		return template.format(self)

	class Meta:
		verbose_name_plural = 'A8. Lista Prezensa'

	